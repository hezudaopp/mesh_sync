# Usage:
#   Server - python tinyp2p.py password server hostname  portnum [otherurl]
#   Client - python tinyp2p.py password client serverurl pattern
#                   argvs[0]   argvs[1] argvs[2] argvs[3] argvs[4] argvs[5]
# Examples:
#   Server - python sync.py hezudaopp server localhost  3337 http://localhost:3337
#   Client - python sync.py hezudaopp client http://localhost:3337 zip

import sys
import os
import SimpleXMLRPCServer
import xmlrpclib
import re
import hmac
# Import libraries used in the program.
# sys : system variables and functions.
# os : portable OS dependent functionalities.
# SimpleXMLRPCServer : basic XML-RPC server framework.
# xmlrpclib : XML-RPC client support.
# re : regular expression support.
# hmac : RFC 2104 Keyed-Hashing Message Authentication.

argvs = sys.argv
password = lambda url : hmac.new(argvs[1], url).hexdigest()
re_search = re.search

# A multiple assignment.
# argvs <- sys.argv : the argument list.
# password <- lambda url:hmac.new(sys.argv[1],url).hexdigest() :
#   a function makes an HMAC digest from a URL.
#   INPUT: a string, url, which is a URL here.
#   OUTPUT: a hexdecimal HMAC digest.
#   DESCRIPTION:
#     1. Creates a HMAC object from the URL using network'server password,
#        sys.argv[1], as the key.
#     2. Returns a hexdecimal digest of the HMAC object.
# re_search <- re.search : alias for the regular expression search function.

ServerProxy = xmlrpclib.ServerProxy
SimpleXMLRPCServer = SimpleXMLRPCServer.SimpleXMLRPCServer
# A multiple assignment.
# ServerProxy <- xmlrpclib.ServerProxy : alias for the ServerProxy class.
# SimpleXMLRPCServer <- SimpleXMLRPCServer.SimpleXMLRPCServer : alias for the SimpleXMLRPCServer class.


def ls(pattern = ""):
    def filter_fun(dir_name):
        if (pattern == ""):
            return True
        else:
            return re_search(pattern, dir_name)
    return filter(filter_fun, os.listdir(os.getcwd()))
#    return filter(lambda n : (pattern == "") or re_search(pattern, n), os.listdir(os.getcwd()))
# a function lists directory entries.
# INPUT: a string, pattern, which is a regular expression pattern.
# OUTPUT: a list of directory entries matched the pattern.
# DESCRIPTION:
#   1. Creates a function using lambda expression that takes a pathname as its
#      parameter. The function returns true if the pattern is empty or the
#      pathname matches the pattern.
#   2. Finds out what is the current working directory.
#   3. Retrieves a list of directory entries of current working directory.
#   4. Filters the list using the lambda function defined.

if argvs[2] != "client":
# Running in server mode...

    myUrl = "http://" + argvs[3] + ":" + argvs[4]
    server_list = argvs[5:]
    srv = lambda server : server.serve_forever()
    # A multiple assignment.
    # myUrl <- "http://"+argvs[3]+":"+argvs[4] : server'server own URL.
    # server_list <- argvs[5:] : URL'server of other servers in the network.
    # srv <- lambda x:x.serve_forever() :
    #   a function to start a SimpleXMLRPCServer.
    #   INPUT: a SimpleXMLRPCServer object, x.
    #   OUTPUT: (none)
    #   DESCRIPTION:
    #     Calls the server'server serve_forever() method to start handling request.



    def update_server_list(servers = []):
        for server in servers:
            if not server in server_list:
                server_list.append(server)
        return server_list
    #    def update_server_list(servers=[]): return ([(server in server_list) or server_list.append(server) for server in servers] or 1) and server_list
    # a function returns the server list.
    # INPUT: a list, servers, of servers' URLs to be added to the server list.
    # OUTPUT: the updated server list.
    # DESCRIPTION:
    #   1. For each URL in servers, checks whether it'server already in the server list.
    #      If it'server not in the list, appends in onto the list.
    #   2. Returns the updated server list.



    def get_file_content(filename):
        fi = file(filename)
        content = fi.read()
        fi.close()
        return content
#    def get_file_content(filename): return ((lambda handle_request: (handle_request.read(), handle_request.close()))(file(filename)))[0]
    # a function returns content of the specified file.
    # INPUT: a string, filename, which is a filename.
    # OUTPUT: the content of the file in a string.
    # DESCRIPTION:
    #   1. Creates a function using lambda expression that takes a file object, handle_request,
    #      as its parameter. The function reads the content of the file, then
    #      closes it. The results of the read and close are put into a tuple, and
    #      the tuple is returned.
    #   2. Creates a file object with the filename. Passes it to the lambda
    #      function.
    #   3. Retrieves and returns the first item returned from the lambda function.


    
    def handle_request(pw, mod, pattern):        
        myUrl_password = password(myUrl)
        if pw == myUrl_password:
            if mod == 0:
                return update_server_list(pattern) 
            elif mod == 1:
                return [ls(pattern)]
            else:
                return get_file_content(pattern)
        else:
            return None
#    handle_request = lambda p, n, a:(p == password(myUrl))and(((n == 0)and update_server_list(a))or((n == 1)and [ls(a)])or get_file_content(a))
    #   a request handling function, depending on the mode, returns server list,
    #   directory entries, or content of a file.
    #   INPUT: a string, p, which is a hexdecimal HMAC digest.
    #          a mode number, n.
    #          if n is 0, a is a list of servers to be added to server list.
    #          if n is 1, a is a pattern string.
    #          if n is anything else, a is a filename.
    #   OUTPUT: if n is 0, returns the server list.
    #           if n is 1, returns directory entries match the pattern.
    #           if n is anything else, returns content of the file.
    #   DESCRIPTION:
    #     1. Verifies the password by comparing the HMAC digest received and the
    #        one created itself. Continues only when they match.
    #     2. If n is 0, calls pr() to add list, a, and returns the result.
    #        If n is 1, calls ls() to list entries match pattern a, and returns
    #        the result enclosed in a list.
    #        If n is any other value, retreives and return content of the file
    #        with filename specified in a.


    
    def aug_network(url):
        if url == myUrl:
            return update_server_list()
        else:
            server = ServerProxy(url)
            server_list = server.handle_request(password(url), 0, update_server_list([myUrl]))
            return update_server_list(server_list)
#    def aug_network(url): return ((url == myUrl) and update_server_list()) or update_server_list(ServerProxy(url).handle_request(password(url), 0, update_server_list([myUrl])))
    # a function augments the network.
    # INPUT: a string, u, which is a URL.
    # OUTPUT: a list of URL'server of servers in the network.
    # DESCRIPTION:
    #   1. If the URL, u, equals to my own URL, just returns the server list.
    #   2. Otherwise, creates a ServerProxy object for server u. Then calls its
    #      request handling function f with a HMAC digest, mode 0, and server
    #      list with myself added.
    #   3. Calls pr() with the result returned from server u to add them to my
    #      own list.
    #   4. Returns the new list.



    servers = update_server_list()
    if servers:
        for server in aug_network(servers[0]):
            aug_network(server)
#    update_server_list() and [aug_network(server) for server in aug_network(update_server_list()[0])]
    # 1. Checks the server list is not empty.
    # 2. Takes the first server on the list. Asks that server to augment its
    #    server list with my URL.
    # 3. For each server on the returned list, asks it to add this server to its
    #    list.



    server = SimpleXMLRPCServer((argvs[3], int(argvs[4])))
    if not server.register_function(handle_request, "handle_request"):
        srv(server)
#    (lambda sv:sv.register_function(handle_request, "handle_request") or srv(sv))(SimpleXMLRPCServer((argvs[3], int(argvs[4]))))
    # Starts request processing.
    # 1. Defines a function with lambda expression that takes a SimpleXMLRPCServer
    #    object, registers request handling function, f, and starts the server.
    # 2. Creates a SimpleXMLRPCServer object using hostname (ar[3]) and portnum
    #    (ar[4]). Then feeds the object to the lambda function.



# Running in client mode...
proxy = ServerProxy(argvs[3])
server_list = proxy.handle_request(password(argvs[3]), 0, [])
for url in server_list:
# 1. Create a ServerProxy object using the serverurl (ar[3]).
# 2. Calls the remote server and retrieves a server list.
# 3. For each URL on the list, do the following:
    proxy = ServerProxy(url)
    filename_list = proxy.handle_request(password(url), 1, argvs[4])
    print filename_list
    for filename in filter(lambda n: not n in ls(), filename_list[0]):
    # 1. Create a ServerProxy object using the URL.
    # 2. Calls the remote server to return a list of filenames matching the
    #    pattern (ar[4]).
    # 3. For each filename doesn't exist locally, do the following:
        proxy_obj = ServerProxy(url)
        file_content = proxy_obj.handle_request(password(url), 2, filename)
        fi = file(filename, "wb")
        if not fi.write(file_content):
            fi.close()
        # 1. Define a lambda function that takes a file object, calls remote server
        #    for the file content, then closes the file.
        # 2. Create a file object in write and binary mode with the filename. (I
        #    think the mode "wc" should be "wb".)
        # 3. Passes the file object to the lambda function.


            
        
#for url in ServerProxy(argvs[3]).handle_request(password(argvs[3]), 0, []):
#    for filename in filter(lambda n:not n in ls(), (ServerProxy(url).handle_request(password(url), 1, argvs[4]))[0]):
#        (lambda fi:fi.write(ServerProxy(url).handle_request(password(url), 2, filename)) or fi.close())(file(filename, "wc"))
