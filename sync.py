import sys
import server
import client

if __name__ == '__main__':
    argvs = sys.argv
    if argvs[2] != "client":
        srv = server.Server(argvs[1], argvs[3], argvs[4], argvs[5:])
    cln = client.Client(argvs[1], argvs[3], argvs[4])
        