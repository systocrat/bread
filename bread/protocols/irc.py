import re

from bread.identify import ProtocolIdentifier


class IRCIdentifier(ProtocolIdentifier):
	def __init__(self):
		super(IRCIdentifier, self).__init__('irc')
		self._re = re.compile(r'(?i)^(user|nick|cap) ')

	def matches(self, data, **kwargs):
		return self._re.match(data.split('\r\n')[0]) is not None

__all__ = [
	'IRCIdentifier'
]