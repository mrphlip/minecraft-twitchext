import time
import base64
import zlib
import json
import urllib.request
import urllib.parse
from constants import CLIENT_ID, LOGIN_URL

TWITCH_API_BASE = 'https://api.twitch.tv/'
TWITCH_SET_CONFIG = TWITCH_API_BASE + 'extensions/%s/configurations/'
TWITCH_SEND_MESSAGE = TWITCH_API_BASE + 'extensions/message/%d'

LAST_TOKEN = None
LAST_DATA = None

EXPIRY_BUFFER = 3600

def get_twitch_data(token):
	global LAST_TOKEN, LAST_DATA

	if token == LAST_TOKEN and LAST_DATA and LAST_DATA['expiry'] - EXPIRY_BUFFER >= time.time():
		return LAST_DATA

	LAST_DATA = _real_get_twitch_data(token)
	LAST_TOKEN = token
	return LAST_DATA

def _real_get_twitch_data(token):
	if not token:
		return {
			'name': 'Not logged in',
			'userid': 0,
			'expiry': 0,
			'jwt': None,
		}

	url = LOGIN_URL + '?' + urllib.parse.urlencode({'token': token})
	with urllib.request.urlopen(url) as fp:
		try:
			data = json.load(fp)
		except json.JSONDecodeError as e:
			data = {'error': 'Not logged in'}

	if 'error' in data:
		return {
			'name': data['error'],
			'userid': 0,
			'expiry': 0,
			'jwt': None,
		}
	else:
		return data

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
	twitchdata = get_twitch_data(token)
	if not twitchdata['jwt']:
		raise ValueError(twitchdata['name'])
	payload = compress_payload(payload)

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
