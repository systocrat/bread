import re

from bread.identify import ProtocolIdentifier


class HttpIdentifier(ProtocolIdentifier):
	def __init__(self):
		super(HttpIdentifier, self).__init__('http')
		self._identify = re.compile(r'(?i)^[A-Z]+ /[^ ]* HTTP/[0-9.]+$')

	def matches(self, data, **kwargs):
		data = data.split('\r\n')[0]
		return self._identify.match(data) is not None

__all__ = [
	'HttpIdentifier'
]