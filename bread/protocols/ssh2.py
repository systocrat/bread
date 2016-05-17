from bread.identify import ProtocolIdentifier


class SSH2Identifier(ProtocolIdentifier):
	def __init__(self):
		super(SSH2Identifier, self).__init__('ssh2')

	def matches(self, data, **kwargs):
		return data.startswith('SSH-2.0-')

__all__ = [
	'SSH2Identifier'
]