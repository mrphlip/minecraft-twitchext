#!/usr/bin/python3

import re
import json
import collections

# data from
# https://minecraft.gamepedia.com/Advancements
# https://minecraft.gamepedia.com/Module:InvSprite
# of a version that matches the 
with open("advancements.txt") as fp:
	ADVANCEMENTS = fp.read()
with open("invsprite.txt") as fp:
	INVSPRITE = fp.read()

# advancements json from a save with all advancements unlocked
# for the criteria data
with open("b23de5f5-14c2-45e8-84db-cb644f465af0.json") as fp:
	CHEEVOS = json.load(fp)

re_advancement = re.compile(r"\{\{\s*Advancements\s*\|((?:[^{}]|\{\{[^{}]*\}\})+?)\s*\}\}", re.I | re.S)
re_junk = re.compile(r'\[\[([^\[\]]*)\]\]|\{\{([^{}]*)\}\}', re.I | re.S)
re_icon = re.compile(r'''^\s*(?:\['([^']+)'\]|\["([^""]+)"\]|(\w+))?\s*=\s*\{[^{}]*\bpos\s*=\s*(\d+)\s*[,}]''', re.I | re.M)

icons = {}
for quotename, doublequotename, shortname, pos in re_icon.findall(INVSPRITE):
	icons[quotename or doublequotename or shortname] = int(pos) - 1

LEVELS = {None: "advancement", "oval": "goal", "fancy": "challenge"}
data = []
for tag in re_advancement.findall(ADVANCEMENTS):
	a = []
	kw = {}
	tag = re_junk.sub((lambda match:(match.group(1) or match.group(2)).replace('|', '-')), tag)
	for i in tag.split('|'):
		if '=' in i:
			k, v = i.split('=', 1)
			kw[k] = v.strip()
		else:
			a.append(i.strip())
	print(a,kw)
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
			for i in CHEEVOS[a[4]]['criteria'].keys()
		],
	}))
print(json.dumps(data, indent=2))
