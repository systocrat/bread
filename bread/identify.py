import re
import six

protocols = dict()

class ProtocolNotFoundException(Exception):
	pass


def identifyProtocol(data):
	for protocol in six.itervalues(protocols):
		if protocol.matches(data):
			return protocol
	raise ProtocolNotFoundException()


class ProtocolIdentifier(object):
	def __init__(self, name):
		self.name = name

	def matches(self, data, **kwargs):
		pass

from bread.protocols.flash import FlashPolicyIdentifier
from bread.protocols.http import HttpIdentifier
from bread.protocols.irc import IRCIdentifier
from bread.protocols.ssh2 import SSH2Identifier

_defaultProtocols = [
	FlashPolicyIdentifier(),
	HttpIdentifier(),
	IRCIdentifier(),
	SSH2Identifier()
]

for proto in _defaultProtocols:
	protocols[proto.name] = proto