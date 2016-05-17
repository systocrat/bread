import sys, time

import six

levels = {
	'debug': 0,
	'info': 1,
	'warning': 2,
	'error': 3,
}

for k,v in six.iteritems(levels):
	setattr(sys.modules[__name__], 'level_%s' % k, v)

symbol_map = {
	level_debug: '?',
	level_info: '*',
	level_warning: '-',
	level_error: '!',
}

class StreamObserver(object):
	def __init__(self, stream, levelarr=None):
		self.stream = stream
		self.levelarr = levelarr

	def msg(self, msg, loglevel):
		if self.levelarr is None or loglevel in self.levelarr:
			self.stream.write(msg + "\n")

class Logger(object):
	def __init__(self, observers=None):
		if observers is None:
			observers = [StreamObserver(sys.stdout)]

		self.observers = observers
		self.time = True
		self.timefmt = '%H:%M:%S'

		def create_func(level):
			def f(self, msg):
				self.__msg(msg, level)
			return f

		for k, v in six.iteritems(levels):
			setattr(self, k, create_func(v))

	def __msg(self, msg, level):
		prefix = ''

		if level in symbol_map:
			p = symbol_map[level]
		else:
			p = 'ERR_UNKSYMBOL'

		# use concatenation instead of format string to allow % as prefix
		prefix = "[" + symbol_map[level] + "] "

		if self.time:
			prefix += '(' + time.strftime(self.timefmt) + ') '

		for x in self.observers:
			x.msg(prefix + msg, level)

	def newline(self, level):
		for x in self.observers:
			x.msg("", level)

	def clean_msg(self, msg, level):
		for x in self.observers:
			x.msg(msg, level)

default_logger = Logger()

def create_func(obj, name):
	def f(msg):
		getattr(obj, name)(obj, msg)
	return f

for k,v in six.iteritems(levels):
	setattr(sys.modules[__name__], k, create_func(default_logger, k))

def newline(level):
	default_logger.newline(level)

def clean_msg(msg, level):
	default_logger.clean_msg(msg, level)