#!/usr/bin/python3

import png
import collections
import json

Image = collections.namedtuple('Image', ['width', 'height', 'image'])
def read_image(filename):
	width, height, data, metadata = png.Reader(filename=filename).asRGBA8()
	data = [list(row) for row in data]
	return Image(width, height, data)

def write_image(image, filename):
	with open(filename, "wb") as fp:
		writer = png.Writer(width=image.width, height=image.height, alpha=True,
			greyscale=False, bitdepth=8)
		writer.write(fp, image.image)

class Spritesheet:
	def __init__(self, filename, iconwidth, iconheight, sheetwidth, sheetheight):
		fullwidth = iconwidth * sheetwidth
		fullheight = iconheight * sheetheight
		if filename is None:
			self.image = Image(fullwidth, fullheight, [[0] * fullwidth * 4 for i in range(fullheight)])
		else:
			self.image = read_image(filename)
			assert self.image.width == iconwidth * sheetwidth
			assert self.image.height == iconheight * sheetheight
		self.iconwidth = iconwidth
		self.iconheight = iconheight
		self.sheetwidth = sheetwidth
		self.sheetheight = sheetheight
		self.iconcount = sheetwidth * sheetheight

	def tile(self, pos):
		if not (0 <= pos < self.iconcount):
			raise ValueError("pos out of bounds: %d" % pos)
		posy, posx = divmod(pos, self.sheetwidth)
		posx *= self.iconwidth
		posy *= self.iconheight
		data = []
		for row in self.image.image[posy:posy + self.iconheight]:
			data.append(row[posx*4:(posx + self.iconwidth)*4])
		return data

	def set_tile(self, pos, data):
		if not (0 <= pos < self.iconcount):
			raise ValueError("pos out of bounds: %d" % pos)
		if len(data) != self.iconheight:
			raise ValueError("tile %d is wrong height" % pos)
		if any(len(row) != self.iconwidth * 4 for row in data):
			raise ValueError("tile %d is wrong width" % pos)
		posy, posx = divmod(pos, self.sheetwidth)
		posx *= self.iconwidth
		posy *= self.iconheight
		for y, row in enumerate(data):
			self.image.image[y + posy][posx*4:(posx + self.iconwidth)*4] = row

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

border_width = data['spritesheet']['tilewidth'] - data['spritesheet']['iconwidth']
border_height = data['spritesheet']['tileheight'] - data['spritesheet']['iconheight']
border_left = border_width // 2
border_right = (border_width + 1) // 2
border_top = border_height // 2
border_bottom = (border_height + 1) // 2

backgrounds = {}
for level, levelfn in [('advancement', 'plain'), ('goal', 'oval'), ('challenge', 'fancy')]:
	for state, statefn in [(False, 'raw'), (True, 'worn')]:
		backgrounds[level, state] = read_image("Advancement-%s-%s.png" % (levelfn, statefn))
		assert backgrounds[level, state].width == data['spritesheet']['tilewidth']
		assert backgrounds[level, state].height == data['spritesheet']['tileheight']

def make_tile(pos, bg):
	tile = raw_sprites.tile(pos)
	border_tile = \
		[[0] * (data['spritesheet']['tilewidth'] * 4) for i in range(border_top)] + \
		[[0] * (border_left * 4) + row + [0] * (border_right * 4) for row in tile] + \
		[[0] * (data['spritesheet']['tilewidth'] * 4) for i in range(border_bottom)]
	if bg is not None:
		composed_tile = []
		for bgrow, row in zip(backgrounds[bg].image, border_tile):
			composed_row = []
			for x in range(0, len(row), 4):
				a = row[x + 3] / 255.0
				composed_row.extend([
					round(bgrow[x + 0] * (1 - a) + row[x + 0] * a),
					round(bgrow[x + 1] * (1 - a) + row[x + 1] * a),
					round(bgrow[x + 2] * (1 - a) + row[x + 2] * a),
					round(bgrow[x + 3] * (1 - a) + row[x + 3]),
				])
			composed_tile.append(composed_row)
		return composed_tile
	else:
		return border_tile

for i, advancement in enumerate(data['advancements']):
	out_sprites.set_tile(i * 2, make_tile(advancement['icon'], (advancement['level'], False)))
	out_sprites.set_tile(i * 2 + 1, make_tile(advancement['icon'], (advancement['level'], True)))
	advancement['icon'] = i * 2

for i, category in enumerate(data['categories']):
	out_sprites.set_tile(i + 2 * len(data['advancements']), make_tile(category['icon'], None))
	category['icon'] = i + 2 * len(data['advancements'])

write_image(out_sprites.image, "spritesheet.png")

data['spritesheet'] = {
	"iconwidth": out_sprites.iconwidth,
	"iconheight": out_sprites.iconwidth,
	"sheetwidth": out_sprites.sheetwidth,
	"sheetheight": out_sprites.sheetheight,
}
with open("advancement_data.json", "w") as fp:
	json.dump(data, fp)
