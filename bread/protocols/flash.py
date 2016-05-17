from bread.identify import ProtocolIdentifier


class FlashPolicyIdentifier(ProtocolIdentifier):
	def __init__(self):
		super(FlashPolicyIdentifier, self).__init__('flash')

	def matches(self, data, **kwargs):
		return data.startswith('<policy-file-request')

__all__ = [
	'FlashPolicyIdentifier'
]