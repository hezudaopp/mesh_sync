import protocol
import logging
import path
import command

class ClientMeshProtocol(protocol.MeshProtocol):
    def connectionMade(self):
        logging.info("Client: Connected to %s." % self.transport.getPeer().host)
        self.pathManager = path.DirManager(path.PathManager.source_dir)
        self.pathManager.make()
        self.command.send_command(self.transport, command.COMMANDS['PULL_REQUEST'])
        
    def dataReceived(self, line):
        protocol.MeshProtocol.dataReceived(self, line)