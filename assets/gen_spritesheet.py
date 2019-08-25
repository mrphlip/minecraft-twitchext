#!/usr/bin/env python3

from PIL import Image
import collections
import json

OUT_PATH = '../extension/public/'

class Spritesheet:
	def __init__(self, filename, iconwidth, iconheight, sheetwidth, sheetheight):
		fullwidth = iconwidth * sheetwidth
		fullheight = iconheight * sheetheight
		if filename is None:
			self.image = Image.new('RGBA', (fullwidth, fullheight), (0, 0, 0, 0))
		else:
			self.image = Image.open(filename)
			assert self.image.width == iconwidth * sheetwidth
			assert self.image.height == iconheight * sheetheight
			assert self.image.mode == 'RGBA'
		self.iconwidth = iconwidth
		self.iconheight = iconheight
		self.sheetwidth = sheetwidth
		self.sheetheight = sheetheight
		self.iconcount = sheetwidth * sheetheight

	def save(self, *args, **kwargs):
		return self.image.save(*args, **kwargs)

	def tile_coords(self, pos):
		if not (0 <= pos < self.iconcount):
			raise ValueError("pos out of bounds: %d" % pos)
		posy, posx = divmod(pos, self.sheetwidth)
		posx *= self.iconwidth
		posy *= self.iconheight
		return posx, posy

	def tile(self, pos):
		posx, posy = self.tile_coords(pos)
		return self.image.crop((posx, posy, posx + self.iconwidth, posy + self.iconheight))

	def set_tile(self, pos, im):
		if im.width != self.iconwidth:
			raise ValueError("tile %d is wrong width" % pos)
		if im.height != self.iconheight:
			raise ValueError("tile %d is wrong height" % pos)
		posx, posy = self.tile_coords(pos)
		self.image.paste(im, (posx, posy, posx + self.iconwidth, posy + self.iconheight))

with open("raw_advancement_data.json") as fp:
	data = json.load(fp)

raw_sprites = Spritesheet("InvSprite.png",
	data['spritesheet']['iconwidth'], data['spritesheet']['iconheight'],
	data['spritesheet']['sheetwidth'], data['spritesheet']['sheetheight'])

gen_tiles = 2 * len(data['advancements']) + len(data['categories'])
gen_width = data['spritesheet']['genwidth']
gen_height = (gen_tiles + gen_width - 1) // gen_width
out_sprites = Spritesheet(None,
	data['spritesheet']['tilewidth'], data['spritesheet']['tileheight'],
	gen_width, gen_height)

border_left = (data['spritesheet']['tilewidth'] - data['spritesheet']['iconwidth']) // 2
border_top = (data['spritesheet']['tileheight'] - data['spritesheet']['iconheight']) // 2
border_coords = (border_left, border_top,
	border_left + data['spritesheet']['iconwidth'],
	border_top + data['spritesheet']['iconheight'])

backgrounds = {}
for level, levelfn in [('advancement', 'plain'), ('goal', 'oval'), ('challenge', 'fancy')]:
	for state, statefn in [(False, 'raw'), (True, 'worn')]:
		backgrounds[level, state] = Image.open("Advancement-%s-%s.png" % (levelfn, statefn))
		assert backgrounds[level, state].width == data['spritesheet']['tilewidth']
		assert backgrounds[level, state].height == data['spritesheet']['tileheight']
		assert backgrounds[level, state].mode == 'RGBA'

def make_tile(pos, bg):
	tile = raw_sprites.tile(pos)
	border_tile = Image.new('RGBA',
		(data['spritesheet']['tilewidth'], data['spritesheet']['tileheight']),
		(0, 0, 0, 0))
	border_tile.paste(tile, border_coords)
	if bg is not None:
		return Image.alpha_composite(backgrounds[bg], border_tile)
	else:
		return border_tile

def css_class(name):
	return name.replace(':', '-').replace('/', '-')

for i, advancement in enumerate(data['advancements']):
	out_sprites.set_tile(i * 2, make_tile(advancement['icon'], (advancement['level'], False)))
	out_sprites.set_tile(i * 2 + 1, make_tile(advancement['icon'], (advancement['level'], True)))
	if len(advancement['criteria']) > 1 and 'mode' not in advancement:
		raise ValueError("Need criteria mode for %s" % advancement['id'])
	del advancement['icon']

for i, category in enumerate(data['categories']):
	out_sprites.set_tile(i + 2 * len(data['advancements']), make_tile(category['icon'], None))
	del category['icon']

out_sprites.save(OUT_PATH+"images/spritesheet.png")

del data['spritesheet']
with open(OUT_PATH+"advancement_data.json", "w") as fp:
	json.dump(data, fp)

with open(OUT_PATH+"spritesheet.css", "w") as fp:
	print(".sprite {", file=fp)
	print("  background: url(images/spritesheet.png) no-repeat;", file=fp)
	print("  width: %dpx;" % out_sprites.iconwidth, file=fp)
	print("  height: %dpx;" % out_sprites.iconheight, file=fp)
	print("  display: inline-block;", file=fp)
	print("  vertical-align: middle;", file=fp)
	print("}", file=fp)
	for i, advancement in enumerate(data['advancements']):
		posx, posy = out_sprites.tile_coords(i * 2)
		print(".sprite.%s {" % css_class(advancement['id']), file=fp)
		print("  background-position: %dpx %dpx;" % (-posx, -posy), file=fp)
		print("}", file=fp)
		posx, posy = out_sprites.tile_coords(i * 2 + 1)
		print(".sprite.%s.done {" % css_class(advancement['id']), file=fp)
		print("  background-position: %dpx %dpx;" % (-posx, -posy), file=fp)
		print("}", file=fp)
	for i, category in enumerate(data['categories']):
		posx, posy = out_sprites.tile_coords(i + 2 * len(data['advancements']))
		print(".sprite.cat-%s {" % css_class(category['id']), file=fp)
		print("  background-position: %dpx %dpx;" % (-posx, -posy), file=fp)
		print("}", file=fp)
