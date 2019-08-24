import json
import base64
import sys
import time
import datetime
import logging
import os
from watchdog.observers import Observer
from watchdog import events
import threading
import queue
from . import twitch
from . import minecraft

DEBOUNCE_TIME = 15

DT_FMT = '%Y-%m-%d %H:%M:%S %z'

def build_payload(config):
	# load advancements data
	with open(config.get_minecraft_filename()) as fp:
		data = json.load(fp)

	# remove all the recipes, we don't care
	data = {
		k: v for k, v in data.items()
		if not k.startswith('minecraft:recipes/')
	}
	# sanity-check schema
	ver = data.pop('DataVersion', None)
	data = {
		advid: {
			'criteria': {
				criteria: datetime.datetime.strptime(date, DT_FMT).timestamp()
				for criteria, date in adv.get('criteria', {}).items()
			},
			'done': adv.get('done', False),
		}
		for advid, adv in data.items()
	}
	if ver:
		data['DataVersion'] = ver

	# add world metadata
	user = minecraft.get_minecraft_user(config.userid)
	icon = minecraft.get_minecraft_icon(config.userid)
	iconurl = "data:image/png;base64," + base64.b64encode(icon).decode("ascii")
	return {
		'world': 	{
			'id': user['id'],
			'name': user['name'],
			'icon': iconurl,
			'world': config.world,
		},
		'advancements': data,
	}

def send_update(config):
	payload = build_payload(config)
	twitch.send_payload(config.twitchtoken, payload)

modification_queue = queue.Queue()
def debounce_thread():
	while True:
		# Wait for a modification
		config = modification_queue.get()
		# If there are more modifications in the queue, get the last one
		try:
			while True:
				config = modification_queue.get_nowait()
		except queue.Empty:
			pass
		# post the update
		send_update(config)
		# Debounce
		time.sleep(DEBOUNCE_TIME)
threading.Thread(target=debounce_thread, daemon=True).start()

observer = Observer()
observer.start()
def set_watched_file(config, mainframe):
	config = config.copy()  # to avoid possible race conditions from aliasing cross-thread
	observer.unschedule_all()
	fullpath = config.get_minecraft_filename()
	path, filename = os.path.split(fullpath)
	handler = EventHandler(filename, config, mainframe)
	if not os.path.isdir(path):
		handler.on_removed()
	else:
		observer.schedule(handler, path, recursive=False)
		if os.path.isfile(fullpath):
			handler.on_modified()
		else:
			handler.on_removed()

class EventHandler:
	def __init__(self, watchfile, config, mainframe):
		self.watchfile = watchfile
		self.config = config
		self.mainframe = mainframe

	def dispatch(self, event):
		if event.is_directory:
			return
		if event.event_type in (events.EVENT_TYPE_CREATED, events.EVENT_TYPE_MODIFIED):
			if os.path.basename(event.src_path) == self.watchfile:
				self.on_modified()
		elif event.event_type == events.EVENT_TYPE_DELETED:
			if os.path.basename(event.src_path) == self.watchfile:
				self.on_removed()
		elif event.event_type == events.EVENT_TYPE_MOVED:
			if os.path.basename(event.dest_path) == self.watchfile:
				self.on_modified()
			elif os.path.basename(event.src_path) == self.watchfile:
				self.on_removed()

	def on_modified(self):
		modification_queue.put(self.config)
		self.mainframe.sent_update()

	def on_removed(self):
		self.mainframe.file_removed()
