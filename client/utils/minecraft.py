import urllib.request
import os
from constants import APP_DIRS
import json
import base64
import time
import functools
from PIL import Image
import io

PROFILE_URL = "https://sessionserver.mojang.com/session/minecraft/profile/%s"

def cached(func, expiry, template, format):
	@functools.wraps(func)
	def wrapper(uid):
		uid = uid.replace('-', '').lower()
		cachefn = os.path.join(APP_DIRS.user_cache_dir, template % uid)
		try:
			stat = os.stat(cachefn)
		except FileNotFoundError:
			pass
		else:
			if stat.st_mtime > time.time() - expiry:
				if format == 'json':
					with open(cachefn, "r") as fp:
						return json.load(fp)
				elif format == 'str':
					with open(cachefn, "r") as fp:
						return fp.read()
				elif format == 'bytes':
					with open(cachefn, "rb") as fp:
						return fp.read()

		data = func(uid)
		os.makedirs(APP_DIRS.user_cache_dir, exist_ok=True)
		if format == 'json':
			with open(cachefn, "w") as fp:
				json.dump(data, fp)
		elif format == 'str':
			with open(cachefn, "w") as fp:
				fp.write(data)
		elif format == 'bytes':
			with open(cachefn, "wb") as fp:
				fp.write(data)
		return data
	return wrapper

def _real_get_minecraft_user(uid):
	try:
		with urllib.request.urlopen(PROFILE_URL % uid) as fp:
			data = json.load(fp)
	except json.JSONDecodeError:
		return {
			'id': uid,
			'name': uid,
			'skinurl': None,
		}
	# {"id":"b23de5f514c245e884dbcb644f465af0","name":"mrphlip","properties":[{"name":"textures","value":"eyJ0aW1lc3RhbXAiOjE1NjYxMzIxMjYwMTIsInByb2ZpbGVJZCI6ImIyM2RlNWY1MTRjMjQ1ZTg4NGRiY2I2NDRmNDY1YWYwIiwicHJvZmlsZU5hbWUiOiJtcnBobGlwIiwidGV4dHVyZXMiOnsiU0tJTiI6eyJ1cmwiOiJodHRwOi8vdGV4dHVyZXMubWluZWNyYWZ0Lm5ldC90ZXh0dXJlLzZkZDhjNDY2Zjk0YzU1ZjM1YjE3ZjEzNTQ2Zjk1MDg4OGE1YmQ5ODFmN2I0MzBiODg1NzY1NDBiNWI4ZWQxN2UifX19"}]}
	properties = {i.get('name'): i.get('value') for i in data.get('properties', [])}
	textures = properties.get('textures')
	textures = textures and json.loads(base64.decodestring(textures.encode("ascii")))
	# {"timestamp":1566132126012,"profileId":"b23de5f514c245e884dbcb644f465af0","profileName":"mrphlip","textures":{"SKIN":{"url":"http://textures.minecraft.net/texture/6dd8c466f94c55f35b17f13546f950888a5bd981f7b430b88576540b5b8ed17e"}}}
	url = textures and textures.get('textures', {}).get('SKIN', {}).get('url')
	return {
		'id': data['id'],
		'name': data['name'],
		'skinurl': url,
	}
get_minecraft_user = cached(_real_get_minecraft_user, 86400, "minecraft_%s.json", "json")

def _real_get_minecraft_skin(uid):
	data = get_minecraft_user(uid)
	if not data.get('skinurl'):
		return b''
	with urllib.request.urlopen(data['skinurl']) as fp:
		return fp.read()
get_minecraft_skin = cached(_real_get_minecraft_skin, 86400*7, "minecraft_skin_%s.png", "bytes")

def _real_get_minecraft_icon(uid):
	img = get_minecraft_skin(uid)
	if not img:
		return b''
	img = Image.open(io.BytesIO(img))
	face = img.crop((8, 8, 16, 16))
	overface = img.crop((40, 8, 48, 16))
	face.alpha_composite(overface)
	facestream = io.BytesIO()
	face.save(facestream, 'png')
	return facestream.getvalue()
get_minecraft_icon = cached(_real_get_minecraft_icon, 3600, "minecraft_icon_%s.png", "bytes")
