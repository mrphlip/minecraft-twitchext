import json
import os
import json
import gzip
from constants import APP_DIRS, DEF_MINECRAFT_DIR
from utils.twitch import get_twitch_data
from utils import nbt

CONFIG_FILE = 'config.json'

class ConfigState:
	def __init__(self, minecraftbase=DEF_MINECRAFT_DIR, world=None, userid=None,
			twitchtoken=None):
		self.minecraftbase = minecraftbase
		self.world = world
		self.userid = userid
		self.twitchtoken = twitchtoken

	def as_dict(self):
		return {
			'minecraftbase': self.minecraftbase,
			'world': self.world,
			'userid': self.userid,
			'twitchtoken': self.twitchtoken,
		}

	@classmethod
	def load(cls):
		try:
			fn = os.path.join(APP_DIRS.user_config_dir, CONFIG_FILE)
			with open(fn, "r") as fp:
				data = json.load(fp)
		except FileNotFoundError:
			return cls()
		else:
			return cls(**data)

	def save(self):
		dir = APP_DIRS.user_config_dir
		fn = os.path.join(dir, CONFIG_FILE)
		os.makedirs(dir, exist_ok=True)
		with open(fn, "w") as fp:
			json.dump(self.as_dict(), fp)

	def copy(self):
		return ConfigState(**self.as_dict())

	def get_minecraft_filename(self):
		if not self.minecraftbase or not self.world or not self.userid:
			raise ValueError("Not configured")
		return os.path.join(self.minecraftbase, 'saves', self.world, 'advancements',
			self.userid + '.json')

	def get_player_filename(self):
		if not self.minecraftbase or not self.world or not self.userid:
			raise ValueError("Not configured")
		return os.path.join(self.minecraftbase, 'saves', self.world, 'playerdata',
			self.userid + '.dat')

	def has_minecraft_config(self):
		#return True
		try:
			path = self.get_minecraft_filename()
		except ValueError:
			return False
		else:
			return os.path.isfile(path)

	def has_twitch_config(self):
		if not self.twitchtoken:
			return False
		return get_twitch_data(self.twitchtoken)['jwt'] is not None

	def get_dataversion(self):
		# load advancements data
		with open(self.get_minecraft_filename()) as fp:
			data = json.load(fp)

		if 'DataVersion' in data:
			return data['DataVersion']

		# Versions 1.12 and 1.13 don't seem to include the data version in the advancements json
		# attenpt to pull it from the main player NBT instead
		try:
			with gzip.open(self.get_player_filename()) as fp:
				data = nbt.load(fp)
			return data.get("DataVersion")
		except (IOError, OSError, ValueError):
			return None
