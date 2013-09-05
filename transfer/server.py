import protocol
import logging

class ServerMeshProtocol(protocol.MeshProtocol):
    def connectionMade(self):
        logging.info('Server: Got connection from %s' % self.transport.getPeer().host)
 
    def connectionLost(self, reason):
        '''what should I do when connection is lost'''
        logging.info('Server: %s disconnected' % self.transport.getPeer().host)
        
    def dataReceived(self, line):
        protocol.MeshProtocol.dataReceived(self, line)
        
