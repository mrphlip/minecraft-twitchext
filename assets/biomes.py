#!/usr/bin/env python3
import zipfile
import json

versions = [
	('1.12', 1139),
	('1.12.1', 1241),
	('1.12.2', 1343),
	('1.13', 1519),
	('1.13.1', 1628),
	('1.13.2', 1631),
	('1.14', 1952),
	('1.14.1', 1957),
	('1.14.2', 1963),
	('1.14.3', 1968),
	('1.14.4', 1976),
	('1.15', 2225),
	('1.15.1', 2227),
	('1.15.2', 2230),
	('1.16', 2566),
	('1.16.1', 2567),
	('1.16.2', 2578),
	('1.16.3', 2580),
	('1.16.4', 2584),
	('1.16.5', 2586),
	('1.17', 2724),
]

biomes = {}
first = True
for ver, dv in versions:
	with zipfile.ZipFile(f"/home/phlip/.local/share/multimc/libraries/com/mojang/minecraft/{ver}/minecraft-{ver}-client.jar") as zfp:
		try:
			with zfp.open("data/minecraft/advancements/adventure/adventuring_time.json") as fp:
				data = json.load(fp)
		except KeyError:
			with zfp.open("assets/minecraft/advancements/adventure/adventuring_time.json") as fp:
				data = json.load(fp)
	criteria = {
		(k if ':' in k else 'minecraft:' + k): v
		for k,v in data['criteria'].items()
	}
	if first:
		for key in criteria:
			biomes[key] = {}
	else:
		for key in criteria:
			if key not in biomes:
				biomes[key] = {'since': dv}
			if key in biomes and biomes[key].get("until"):
				raise ValueError(f"Biome {key} went away and came back?")
		for key in biomes:
			if key not in criteria and not biomes[key].get("until"):
				biomes[key]['until'] = dv
	first = False

biome_list = []
for key in sorted(biomes):
	biome = biomes[key]
	name = key
	if name.startswith("minecraft:"):
		name = name[10:]
	name = name.replace("_"," ").title()
	newdict = {
		'id': key,
		'description': name,
	}
	if biome.get('since'):
		newdict['since'] = biome['since']
	if biome.get('until'):
		newdict['until'] = biome['until']
	biome_list.append(newdict)
print(json.dumps(biome_list, indent=2))
