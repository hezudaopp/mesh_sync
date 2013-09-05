import xmlrpclib
import utils
import _file

ServerProxy = xmlrpclib.ServerProxy

class Client(object):
    def __init__(self, password, url, pattern):
        self.password = password
        self.url = url
        self.pattern = pattern
        # 1. Create a ServerProxy object using the serverurl (ar[3]).
        # 2. Calls the remote server and retrieves a server list.
        # 3. For each URL on the list, do the following:
        proxy = ServerProxy(self.url)
        server_list = proxy.handle_request(utils.gen_pw(self.password, self.url), 0, [])
        for url in server_list:
            # 1. Create a ServerProxy object using the URL.
            # 2. Calls the remote server to return a list of filenames matching the
            #    pattern (ar[4]).
            # 3. For each filename doesn't exist locally, do the following:
            proxy = ServerProxy(self.url)
            remote_list = proxy.handle_request(utils.gen_pw(self.password, self.url), 1, self.pattern)
            remote_filename_list = remote_list[0][0]
            remote_dir_list = remote_list[0][1]
            local_list = utils.ls()
            local_filename_list = local_list[0]
            local_dir_list = local_list[1]
            proxy_obj = ServerProxy(url)
            for dirname in filter(lambda n: not n in local_dir_list, remote_dir_list):
                print dirname
                file_proxy = _file.FileProxy(dirname)
                file_proxy.make_dir()
            
            for filename in filter(lambda n: not n in local_filename_list, remote_filename_list):
                '''For each filename doesn't exist locally, do the following:'''
                print filename
                file_proxy = _file.FileProxy(filename)
                with file_proxy.open_file("wb") as handle:
                    handle.write(proxy_obj.handle_request(utils.gen_pw(self.password, self.url), 2, filename).data)