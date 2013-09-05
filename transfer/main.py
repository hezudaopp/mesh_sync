from twisted.internet import protocol, reactor
import logging
from client import ClientMeshProtocol as ClientProtocol
from server import ServerMeshProtocol as ServerProtocol
import db
import path
#import path
#from SimpleXMLRPCServer import SimpleXMLRPCServer
#from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

HOST = "localhost"
PORT = 3336

LOG_FILENAME = 'connection.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

class BasicClientFactory(protocol.ClientFactory):
    protocol = ClientProtocol
    clientConnectionLost = clientConnectionFailed = \
    lambda self, connection, reason: reactor.stop()

if __name__ == '__main__':
    factory = protocol.Factory()
    factory.protocol = ServerProtocol
    reactor.connectTCP(HOST, PORT, BasicClientFactory())
    logging.info("Server: waiting for connection")
    db = db.Db()
    db.create_tables()
    pathManager = path.DirManager()
    pathManager.db_init()
    reactor.listenTCP(PORT, factory)
    reactor.run()
#    # Restrict to a particular path.
#    class RequestHandler(SimpleXMLRPCRequestHandler):
#        rpc_paths = ('/RPC2',)
    # Create server
#    server = SimpleXMLRPCServer(("localhost", 3337),
#                                requestHandler=RequestHandler)
#    server.register_introspection_functions()
#    server.register_instance(path.FileManager(), True)
#    server.register_instance(path.DirManager(), True)
#    server.register_function(adder_function, 'add')
#    # Run the server's main loop
#    server.serve_forever()