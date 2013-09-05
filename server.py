import utils
import SimpleXMLRPCServer
import xmlrpclib
import _file

ServerProxy = xmlrpclib.ServerProxy
SimpleXMLRPCServer = SimpleXMLRPCServer.SimpleXMLRPCServer

class Server(object):
    def __init__(self, password, hostname, port, server_list):
        self.password = password
        self.myUrl = "http://" + hostname + ":" + port
        self.server_list = server_list
        servers = self.update_server_list()
        if servers:
            for server in self.aug_network(servers[0]):
                self.aug_network(server)
        server = SimpleXMLRPCServer((hostname, int(port)))
        if not server.register_function(self.handle_request, "handle_request"):
            utils.srv(server)
    
    def update_server_list(self, servers = []):
        for server in servers:
            if not server in self.server_list:
                self.server_list.append(server)
        return self.server_list
    
    def get_file_content(self, filename):
        file_proxy = _file.FileProxy(filename)
        with file_proxy.open_file("rb") as handle:
            return xmlrpclib.Binary(handle.read())
    
    def handle_request(self, pw, mod, pattern):        
        myUrl_password = utils.gen_pw(self.password, self.myUrl)
        if pw == myUrl_password:
            if mod == 0:
                return self.update_server_list(pattern) 
            elif mod == 1:
                return [utils.ls(pattern)]
            else:
                return self.get_file_content(pattern)
        else:
            return None

    def aug_network(self, url):
        if url == self.myUrl:
            return self.update_server_list()
        else:
            server = ServerProxy(url)
            server_list = server.handle_request(utils.gen_pw(url), 0, self.update_server_list([self.myUrl]))
            return self.update_server_list(server_list)