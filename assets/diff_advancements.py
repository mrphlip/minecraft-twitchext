#!/usr/bin/env python3
import json
import os

with open("raw_advancement_data.json") as fp:
	old = json.load(fp)
with open("new_advancement_data.json") as fp:
	new = json.load(fp)

def dump_advancements(advs, fp):
	for adv in sorted(advs, key=lambda a:a['id']):
		for k in sorted(adv.keys()):
			print(f"{adv['id']}::{k}: {adv[k]}", file=fp)

with open("/tmp/1", "w") as fp:
	dump_advancements(old['advancements'], fp)
with open("/tmp/2", "w") as fp:
	dump_advancements(new, fp)

os.system("diff /tmp/1 /tmp/2")
