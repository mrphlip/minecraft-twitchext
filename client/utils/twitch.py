import time
import base64
import zlib
import json
import urllib.request
from constants import CLIENT_ID

TWITCH_API_BASE = 'https://api.twitch.tv/'
TWITCH_SET_CONFIG = TWITCH_API_BASE + 'extensions/%s/configurations/'
TWITCH_SEND_MESSAGE = TWITCH_API_BASE + 'extensions/message/%d'

LAST_TOKEN = None
LAST_DATA = None

EXPIRY_BUFFER = 3600

def get_twitch_data(token):
	global LAST_TOKEN, LAST_DATA

	if not token:
		return {'name': 'Not logged in', 'userid': 0, 'expiry': 0, 'jwt': None}

	if token == LAST_TOKEN and LAST_DATA and LAST_DATA['expiry'] - EXPIRY_BUFFER >= time.time():
		return LAST_DATA

	LAST_DATA = _real_get_twitch_data(token)
	LAST_TOKEN = token
	return LAST_DATA

def _real_get_twitch_data(token):
	# Just a hard-coded stub until I build the login flow
	import jwt
	with open("secret.txt") as fp:
		secret = fp.read()
	secret = base64.decodestring(secret.encode("ascii"))
	userid = 25875159
	name = 'MrPhlip'
	expiry = int(time.time() + 86400)

	payload = {
		'channel_id': "%d" % userid,
		'exp': expiry,
		'pubsub_perms': {'send': ['broadcast']},
		'role': 'external',
		'user_id': "%d" % userid,
		'opaque_user_id': "U%d" % userid,
	}
	return {
		'name': name,
		'userid': userid,
		'expiry': expiry,
		'jwt': jwt.encode(payload, secret).decode('ascii'),
	}

def compress_payload(payload):
	payload = json.dumps(payload, separators=(',', ':'), ensure_ascii=True)
	compress = zlib.compressobj(
		level=zlib.Z_BEST_COMPRESSION,
		wbits=-zlib.MAX_WBITS,  # negative = no header, raw inflate stream
	)
	deflated = compress.compress(payload.encode('ascii'))
	deflated += compress.flush()
	return base64.b64encode(deflated).decode("ascii")

def send_payload(token, payload):
	if not token:
		raise ValueError("Not logged in")
	payload = compress_payload(payload)
	twitchdata = get_twitch_data(token)

	with urllib.request.urlopen(urllib.request.Request(
			TWITCH_SET_CONFIG % CLIENT_ID,
			json.dumps({
				'segment': "broadcaster",
				'channel_id': twitchdata['userid'],
				'version': 1,
				'content': payload,
			}).encode("utf-8"),
			headers={
				'Authorization': "Bearer %s" % twitchdata['jwt'],
				'Client-Id': CLIENT_ID,
				'Content-type': "application/json",
			},
			method='PUT')) as fp:
		pass

	with urllib.request.urlopen(urllib.request.Request(
			TWITCH_SEND_MESSAGE % twitchdata['userid'],
			json.dumps({
				'content_type': "text/plain",
				'message': payload,
				'targets': ["broadcast"],
			}).encode("utf-8"),
			headers={
				'Authorization': "Bearer %s" % twitchdata['jwt'],
				'Client-Id': CLIENT_ID,
				'Content-type': "application/json"
			},
			method='POST')) as fp:
		pass
