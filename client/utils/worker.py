import json
import base64
from . import twitch
from . import minecraft

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
	for k, v in data.items():
		if k != 'DataVersion':
			v.setdefault('criteria', {})
			v.setdefault('done', False)

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
