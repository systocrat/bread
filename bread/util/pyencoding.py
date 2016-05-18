from _codecs import utf_8_decode
import struct

import six

big_endian, little_endian = range(2)

packEndians = {
	big_endian: '>',
	little_endian: '<'
}


# thrown when there isn't enough data
class ReadException(Exception):
	pass


# endian is here for automatic struct.packing purposes
def packByte(b, endian=big_endian):
	return struct.pack('%sB' % packEndians[endian], b)


def packSByte(endian=big_endian):
	return struct.pack('%sb' % packEndians[endian], b)


def packShort(endian=big_endian):
	return struct.pack('%sh' % packEndians[endian], s)


def packUShort(s, endian=big_endian):
	return struct.pack('%sH' % packEndians[endian], s)


def packInt(i, endian=big_endian):
	return struct.pack('%si' % packEndians[endian], i)


def packUInt(i, endian=big_endian):
	return struct.pack('%sI' % packEndians[endian], i)


def packLong(i, endian=big_endian):
	return struct.pack('%sq' % packEndians[endian], i)


def packULong(i, endian=big_endian):
	return struct.pack('%sQ' % packEndians[endian], i)


# All of the names of the compiled structs on the reader object
# This makes dealing with endians faster
compiled_struct_names = [
	('struct_sbyte', '%sb'),
	('struct_short', '%sh'),
	('struct_ushort', '%sH'),
	('struct_int', '%si'),
	('struct_uint', '%sI'),
	('struct_long', '%sq'),
	('struct_ulong', '%sQ'),
	('struct_float', '%sf'),
	('struct_double', '%sd'),
	('struct_bool', '%s?'),
]


class Reader(object):
	def __init__(self, data=None, endian=big_endian):
		self.index = 0
		self.endian = packEndians[endian]

		for (struct_name, struct_prototype) in compiled_struct_names:
			setattr(self, struct_name, struct.Struct(struct_prototype % self.endian))

		if data is None:
			self.data = ''
		else:
			self.data = data

	def addData(self, data):
		self.data += data

	def has(self, c):
		return len(self.data) - self.index >= c

	def advance(self, c):
		self.index += c

	def revert(self):
		self.index = 0

	def commit(self):
		self.data = self.data[self.index:]
		self.index = 0

	def empty(self):
		self.data = ''
		self.index = 0

	def peekByte(self):
		if not self.has(1):
			raise ReadException()

		return ord(self.data[self.index])

	def readByte(self):
		if not self.has(1):
			raise ReadException()

		self.advance(1)
		return ord(self.data[self.index - 1])

	def readSByte(self):
		if not self.has(1):
			raise ReadException()

		self.advance(1)
		return self.struct_sbyte.unpack_from(self.data, self.index - 1)[0]

	def readChars(self, count):
		if not self.has(count):
			raise ReadException()

		self.advance(count)
		return self.data[self.index - count:self.index]

	def readBytes(self, count):
		if not self.has(count):
			raise ReadException()

		self.advance(count)
		return [ord(x) for x in list(self.data[self.index - count:self.index])]

	def readChar(self):
		if not self.has(1):
			raise ReadException()

		self.advance(1)
		return chr(self.data[self.index - 1])

	def readShort(self):
		if not self.has(2):
			raise ReadException()

		self.advance(2)
		return self.struct_short.unpack_from(self.data, self.index - 2)[0]

	def readUShort(self):
		if not self.has(2):
			raise ReadException()

		self.advance(2)
		return self.struct_ushort.unpack_from(self.data, self.index - 2)[0]

	def readInt(self):
		if not self.has(4):
			raise ReadException()

		self.advance(4)
		return self.struct_int.unpack_from(self.data, self.index - 4)[0]

	def readUInt(self):
		if not self.has(4):
			raise ReadException()
		self.advance(4)
		return self.struct_uint.unpack_from(self.data, self.index - 4)[0]

	def readLong(self):
		if not self.has(8):
			raise ReadException()

		self.advance(8)
		return self.struct_long.unpack_from(self.data, self.index - 8)[0]

	def readULong(self):
		if not self.has(8):
			raise ReadException()
		self.advance(8)
		return self.struct_ulong.unpack_from(self.data, self.index - 8)[0]

	def readFloat(self):
		if not self.has(4):
			raise ReadException()

		self.advance(4)
		return self.struct_float.unpack_from(self.data, self.index - 4)[0]

	def readDouble(self):
		if not self.has(8):
			raise ReadException()

		self.advance(8)
		return self.struct_double.unpack_from(self.data, self.index - 8)[0]

	def readBool(self):
		if not self.has(1):
			raise ReadException()

		self.advance(1)
		return self.struct_bool.unpack_from(self.data, self.index - 1)[0]

	def readCharArray(self, len_func):
		if hasattr(len_func, '__call__'):
			l = len_func()
		else:
			l = len_func

		return self.readChars(l)

	def readArray(self, len_func, data_func, data_len=None):
		if hasattr(len_func, '__call__'):
			l = len_func()
		else:
			l = len_func

		if data_len is not None and not self.has(l * data_len):
			raise ReadException()

		ret = []

		for _ in six.moves.xrange(l):
			ret.append(data_func())

		return ret

	def readUTF8(self):
		l = self.readUShort()

		if not self.has(l):
			raise ReadException()

		ret = utf_8_decode(self.data[self.index:self.index + l])[0]
		self.advance(l)
		return ret
