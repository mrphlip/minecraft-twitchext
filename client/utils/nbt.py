import struct

TAG_End = 0
TAG_Byte = 1
TAG_Short = 2
TAG_Int = 3
TAG_Long = 4
TAG_Float = 5
TAG_Double = 6
TAG_Byte_Array = 7
TAG_String = 8
TAG_List = 9
TAG_Compound = 10
TAG_Int_Array = 11
TAG_Long_Array = 12

def _encstr(s):
	s = s.encode("utf-8")
	return struct.pack('>H', len(s)) + s
def _decstr(s):
	l = struct.unpack(">H", s[:2])[0]
	return s[2:2+l].decode("utf-8"), s[2+l:]

class NBT():
	"""Base class for NBT objects"""
	TAG = None
	_types = None

	@classmethod
	def type(cls, tag):
		"""Get the specific class for a given NBT type tag"""
		if cls._types is None:
			cls._types = {i.TAG: i for i in cls.__subclasses__()}
		return cls._types[tag]

	def as_nbt(self, name=''):
		"""Serialise an object to NBT bytes"""
		return struct.pack('>b', self.TAG) + _encstr(name) + self.as_payload()

	@classmethod
	def from_nbt(cls, data):
		"""Deserialise an object from NBT bytes"""
		tag = struct.unpack('>b', data[:1])[0]
		if cls.TAG is not None and tag != cls.TAG:
			raise ValueError("Incorrect type tag")
		name, payload = _decstr(data[1:])
		val, rest = cls.type(tag).from_payload(payload)
		return name, val, rest

	def as_payload(self):
		"""Serialise the payload component of an NBT object"""
		raise NotImplemented

	@classmethod
	def from_payload(cls, data):
		"""Deserialise the payload component of an NBT object"""
		raise NotImplemented

class Byte(int, NBT):
	TAG = TAG_Byte
	def as_payload(self):
		return struct.pack('>b', self)
	def __str__(self):
		return int.__str__(self) + "b"
	@classmethod
	def from_payload(cls, data):
		return Byte(struct.unpack('>b', data[:1])[0]), data[1:]

class Short(int, NBT):
	TAG = TAG_Short
	def as_payload(self):
		return struct.pack('>h', self)
	def __str__(self):
		return int.__str__(self) + f"s"
	@classmethod
	def from_payload(cls, data):
		return Short(struct.unpack('>h', data[:2])[0]), data[2:]

class Int(int, NBT):
	TAG = TAG_Int
	def as_payload(self):
		return struct.pack('>i', self)
	def __str__(self):
		return int.__str__(self)
	@classmethod
	def from_payload(cls, data):
		return Int(struct.unpack('>i', data[:4])[0]), data[4:]

class Long(int, NBT):
	TAG = TAG_Long
	def as_payload(self):
		return struct.pack('>q', self)
	def __str__(self):
		return int.__str__(self) + "l"
	@classmethod
	def from_payload(cls, data):
		return Long(struct.unpack('>q', data[:8])[0]), data[8:]

class Float(float, NBT):
	TAG = TAG_Float
	def as_payload(self):
		return struct.pack('>f', self)
	def __str__(self):
		return float.__str__(self) + f"f"
	@classmethod
	def from_payload(cls, data):
		return Float(struct.unpack('>f', data[:4])[0]), data[4:]

class Double(float, NBT):
	TAG = TAG_Double
	def as_payload(self):
		return struct.pack('>d', self)
	def __str__(self):
		return float.__str__(self)
	@classmethod
	def from_payload(cls, data):
		return Double(struct.unpack('>d', data[:8])[0]), data[8:]

class ByteArray(bytes, NBT):
	TAG = TAG_Byte_Array
	def as_payload(self):
		return struct.pack(f'>I{len(self)}B', len(self), *self)
	def __str__(self):
		return f'[B;{",".join(str(i) for i in self)}]'
	@classmethod
	def from_payload(cls, data):
		l = struct.unpack(">I", data[:4])[0]
		return ByteArray(struct.unpack(f'>{l}B', data[4:4+l])), data[4+l:]

class String(str, NBT):
	TAG = TAG_String
	def as_payload(self):
		return _encstr(self)
	def __str__(self):
		if self.isalnum():
			return str.__str__(self)
		else:
			return str.__repr__(self)
	@classmethod
	def from_payload(cls, data):
		return _decstr(data)

class List(list, NBT):
	TAG = TAG_List
	def as_payload(self):
		if self:
			tag = self[0].TAG
		else:
			tag = TAG_End
		if not all(i.TAG == tag for i in self):
			raise ValueError("List values not all same type")
		return struct.pack('>bI', tag, len(self)) + b''.join(i.as_payload() for i in self)
	def __str__(self):
		return f'[{",".join(str(i) for i in self)}]'
	@classmethod
	def from_payload(cls, data):
		tag, l = struct.unpack(">bI", data[:5])
		data = data[5:]
		if l == 0:
			return List([]), data
		typecls = NBT.type(tag)
		res = []
		for i in range(l):
			val, data = typecls.from_payload(data)
			res.append(val)
		return List(res), data

class Compound(dict, NBT):
	TAG = TAG_Compound
	def as_payload(self):
		return b''.join(v.as_nbt(k) for k,v in self.items()) + struct.pack('>b', TAG_End)
	def __str__(self):
		return '{' + ','.join(f"{k}:{v}" for k,v in self.items()) + '}'
	@classmethod
	def from_payload(cls, data):
		res = {}
		while data and struct.unpack('>b', data[:1])[0] != TAG_End:
			name, val, data = NBT.from_nbt(data)
			res[name] = val
		return Compound(res), data[1:]

class IntArray(list, NBT):
	TAG = TAG_Int_Array
	def as_payload(self):
		return struct.pack(f'>I{len(self)}i', len(self), *self)
	def __str__(self):
		return f'[I;{",".join(str(i) for i in self)}]'
	@classmethod
	def from_payload(cls, data):
		l = struct.unpack(">I", data[:4])[0]
		return IntArray(struct.unpack(f'>{l}i', data[4:4+4*l])), data[4+4*l:]

class LongArray(list, NBT):
	TAG = TAG_Long_Array
	def as_payload(self):
		return struct.pack(f'>I{len(self)}q', len(self), *self)
	def __str__(self):
		return f'[L;{",".join(str(i) for i in self)}]'
	@classmethod
	def from_payload(cls, data):
		l = struct.unpack(">I", data[:4])[0]
		return LongArray(struct.unpack(f'>{l}q', data[4:4+8*l])), data[4+8*l:]

def loads(data):
	name, val, rest = NBT.from_nbt(data)
	if rest:
		raise ValueError("Junk after NBT data")
	return val

def load(fp):
	return loads(fp.read())

def dumps(obj):
	return obj.as_nbt()
