from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from twisted.internet.protocol import connectionDone

import config
import klogging
from bread.identify import identifyProtocol, ProtocolNotFoundException


class _BreadInternalClientProtocol(protocol.Protocol):
	def __init__(self):
		self.factory = None  # type: _BreadInternalClientFactory

	def connectionMade(self):
		self.factory.connectionMade.callback(self)

	def dataReceived(self, data):
		self.factory.dataReceived(data)

	def connectionLost(self, reason=connectionDone):
		self.factory.connectionLost.callback(reason)


class _BreadInternalClientFactory(protocol.Factory):
	def __init__(self, dataReceived):
		self.dataReceived = dataReceived
		self.connectionMade = Deferred()
		self.connectionLost = Deferred()

	def buildProtocol(self, addr):
		b = _BreadInternalClientProtocol()
		b.factory = self
		return b

class BreadServerProtocol(protocol.Protocol):
	def __init__(self):
		self.factory = None  # type: BreadServerFactory
		self._clientFactory = _BreadInternalClientFactory(self._clientDataReceived)
		self._clientFactory.connectionMade.addCallback(self._clientConnectionMade)
		self._clientFactory.connectionLost.addCallback(self._clientConnectionLost)
		self._client = None
		self._data = ''
		self._recv = False
		self._localClose = False

	def dataReceived(self, data):
		if not self._recv:
			try:
				proto = identifyProtocol(data)
				klogging.info('ProtocolIdentifier identified: {0}'.format(proto.name))
				if not self.factory.mappings.has_key(proto.name):
					klogging.error('ProtocolIdentifier with name {0} not mapped.'.format(proto.name))
					self.transport.abortConnection()
					return
				host, port = self.factory.mappings[proto.name]
				klogging.info('Local port: {0}'.format(port))
				endpoint = TCP4ClientEndpoint(reactor, host, port, self.factory.localTimeout)

				connect = endpoint.connect(self._clientFactory)
				connect.addErrback(self._failedLocalConnection)
				self._recv = True
				self._data += data
			except ProtocolNotFoundException:
				klogging.error('ProtocolIdentifier not found!')
				self.transport.abortConnection()
				return
		elif self._recv and self._client is None:
			self._data += data
		else:
			self._client.transport.write(data)

	def connectionLost(self, reason=connectionDone):
		if not self._localClose and self._client is not None:
			self._client.transport.abortConnection()
		klogging.info('Finished forwarding proxy.')

	def _failedLocalConnection(self, err):
		klogging.error('Failed local connection: {0}'.format(repr(err)))
		self.transport.abortConnection()

	def _clientConnectionMade(self, protocol):
		klogging.info('Local client connection made!')
		self._client = protocol
		protocol.transport.write(self._data)
		self._data = ''

	def _clientConnectionLost(self, reason):
		klogging.info('Local client connection lost!')
		self._localClose = True
		self.transport.loseConnection()

	def _clientDataReceived(self, data):
		klogging.info('Local client data length: {0}'.format(len(data)))
		self.transport.write(data)


class BreadServerFactory(protocol.Factory):
	def __init__(self, mappings=None, localTimeout=30):
		self.mappings = mappings or dict()
		self.localTimeout = localTimeout

	def buildProtocol(self, addr):
		b = BreadServerProtocol()
		b.factory = self
		return b


if __name__ == '__main__':
	fac = BreadServerFactory(config.forwards, 40)
	local = TCP4ServerEndpoint(reactor, config.localPort, interface='0.0.0.0')
	local.listen(fac)
	reactor.run()