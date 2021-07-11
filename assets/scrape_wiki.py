#!/usr/bin/env python3

import re
import json
import collections

# data from
# https://minecraft.gamepedia.com/Advancements
# https://minecraft.gamepedia.com/Module:InvSprite
#   of a version that matches the https://minecraft.fandom.com/wiki/File:InvSprite.png
# https://minecraft.fandom.com/wiki/Module:Protocol_version/Versions
with open("advancements.txt") as fp:
	ADVANCEMENTS = fp.read()
with open("invsprite.txt") as fp:
	INVSPRITE = fp.read()
with open("dataversion.txt") as fp:
	DATAVERSION = fp.read()

# advancements json from a save with all advancements unlocked
# for the criteria data
with open("b23de5f5-14c2-45e8-84db-cb644f465af0.json") as fp:
	CHEEVOS = json.load(fp)

re_advancement = re.compile(r"\{\{\s*Advancements\s*\|((?:[^{}]|\{\{(?:[^{}]|\{\{[^{}]*\}\})*\}\})+?)\s*\}\}", re.I | re.S)
re_junk = re.compile(r'\[\[([^\[\]]*)\]\]|\{\{([^{}]*)\}\}', re.I | re.S)
re_icon = re.compile(r'''^\s*(?:\['([^']+)'\]|\["([^""]+)"\]|(\w+))?\s*=\s*\{[^{}]*\bpos\s*=\s*(\d+)\s*[,}]''', re.I | re.M)

icons = {}
for quotename, doublequotename, shortname, pos in re_icon.findall(INVSPRITE):
	icons[quotename or doublequotename or shortname] = int(pos) - 1

LEVELS = {"plain": "advancement", "oval": "goal", "fancy": "challenge"}
data = []
for tag in re_advancement.findall(ADVANCEMENTS):
	a = []
	kw = {}
	old_tag = None
	while old_tag != tag:
		old_tag = tag
		tag = re_junk.sub((lambda match:(match.group(1) or match.group(2)).replace('|', '-').replace('=', '-')), tag)
	for i in tag.split('|'):
		if '=' in i:
			k, v = i.split('=', 1)
			kw[k] = v.strip()
		else:
			a.append(i.strip())
	if a[0].endswith(".gif"):
		a[0] = a[0][:-4]
	if ':' not in a[4]:
		a[4] = "minecraft:" + a[4]
	#print(a,kw)
	data.append(collections.OrderedDict({
		"id": a[4],
		"category": a[4].split('/', 1)[0],
		"name": kw['title'],
		"description": a[1],
		"icon": icons[a[0]],
		"level": LEVELS[kw.get('bg')],
		"criteria": [
			collections.OrderedDict({
				"id": i,
				"description": i.replace('minecraft:', '').replace('_', ' ').title(),
			})
			for i in sorted(CHEEVOS[a[4]]['criteria'].keys())
		],
	}))
with open("new_advancement_data.json", "w") as fp:
	json.dump(data, fp, indent=2)

# generate data version data
MIN_VERSION = 1139
re_version = re.compile(r"ver\s*\(\s*(?:java|java_old|java_af)\s*,\s*'([^']*)'\s*,[^,]*,\s*(\d+)\s*\)")
versions = {}
for ver in re_version.findall(DATAVERSION):
	name, dv = ver
	dv = int(dv)
	if dv >= MIN_VERSION:
		versions[dv] = name
with open("data_versions.json", "w") as fp:
	json.dump(versions, fp, indent=2)
with open("../extension/public/data_versions.json", "w") as fp:
	json.dump(versions, fp, indent=2)
