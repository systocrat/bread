from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString, TCP4ServerEndpoint
from twisted.internet.protocol import connectionDone
from twisted.python import log

import config
from bread.identify import identifyProtocol, ProtocolNotFoundException


# Thanks glyph!
class PeeredConnection(protocol.Protocol):
	noisy = True
	peer = None

	def connectionLost(self, reason=connectionDone):
		if self.peer is not None:
			self.peer.transport.loseConnection()
			self.peer = None
		elif self.noisy:
			log.msg('Unable to connect to peer: {0}'.format(reason))

	def dataReceived(self, data):
		self.peer.transport.write(data)

class _BreadInternalProxyClient(PeeredConnection):
	def connectionMade(self):
		self.peer.peer = self

		# This hooks up the peer transport and our own transport for flow control
		# This stops connections from filling proxy memory when one side produces too much data
		# faster than the other can consume
		# Reference: https://github.com/twisted/twisted/blob/2a6c7818ae18bd56ba2406d0a2f01b723bc5dc62/twisted/protocols/portforward.py#L35-L43
		self.transport.registerProducer(self.peer.transport, True)
		self.peer.transport.registerProducer(self.transport, True)

		self.peer.transport.resumeProducing()


class _BreadInternalClientFactory(protocol.ClientFactory):
	protocol = _BreadInternalProxyClient

	def __init__(self, server):
		self.server = server

	def buildProtocol(self, addr):
		prot = protocol.ClientFactory.buildProtocol(self, addr)
		prot.peer = self.server
		return prot

	def clientConnectionFailed(self, connector, reason):
		self.server.transport.loseConnection()


class BreadServerProtocol(PeeredConnection):
	noisy = True

	def __init__(self):
		self.factory = None  # type: BreadServerFactory
		self._clientFactory = _BreadInternalClientFactory(self)
		self._client = None
		self._recv = False  # whether we've received data or not this instance

	def dataReceived(self, data):
		if self._recv:
			PeeredConnection.dataReceived(self, data)
			return
		self._recv = True
		self.transport.pauseProducing()
		try:
			proto = identifyProtocol(data)
			if self.noisy:
				log.msg('ProtocolIdentifier identified: {0}'.format(proto.name))

			if not self.factory.mappings.has_key(proto.name):
				if self.noisy:
					log.msg('ProtocolIdentifier with name {0} not mapped.'.format(proto.name))
				self.transport.abortConnection()
				return
			# build our endpoint from the config
			endpoint = clientFromString(reactor, self.factory.mappings[proto.name])

			if self.noisy:
				log.msg('External endpoint built for protocol {0}: {1}'.format(proto.name, repr(endpoint)))

			connect = endpoint.connect(self._clientFactory)
			connect.addCallback(self._onLocalConnection, data)
			connect.addErrback(self._failedLocalConnection)
		except ProtocolNotFoundException:
			if self.noisy:
				log.msg('ProtocolIdentifier not found!')

			self.transport.loseConnection()
			return

	def _onLocalConnection(self, protocol, data):
		protocol.transport.write(data)
		return protocol

	def _failedLocalConnection(self, err):
		log.msg('Reverse proxy connection failed: {0}'.format(err))
		self.transport.loseConnection()


class BreadServerFactory(protocol.ServerFactory):
	protocol = BreadServerProtocol

	def __init__(self, mappings=None, localTimeout=30):
		self.mappings = mappings or dict()
		self.localTimeout = localTimeout

if __name__ == '__main__':
	import sys
	log.startLogging(sys.stdout)
	fac = BreadServerFactory(config.forwards, 40)
	local = TCP4ServerEndpoint(reactor, config.localPort, interface='0.0.0.0')
	local.listen(fac)
	reactor.run()