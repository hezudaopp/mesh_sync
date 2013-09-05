import os
import logging
import ast
import path

CMD_BEGIN = "CMD_BEGIN"
CMD_END = "CMD_END"
FILE_BEGIN = "FILE_BEGIN"
FILE_END = "FILE_END"
COMMANDS = {'PULL_REQUEST':'PullRequest', 'PULL_RESPONSE':'PullResponse', \
            'SYNC_REQUEST':'SyncRequest', 'SYNC_RESPONSE_FILE':'SyncResponseFile', \
            'SYNC_RESPONSE_DIR':'SyncResponseDir', 'SYNC_RESPONSE_FINISH':'SyncResponseFinish', \
            'FILE_INFO_REQUEST':'FileInfoRequest', 'FILE_INFO_RESPONSE':'FileInfoResponse', \
            'FILE_INFO_CONFIRM':'FileInfoConfirm'}

class Command(object):
    send_command = lambda self, transport, cmd : transport.write(CMD_BEGIN + cmd + CMD_END)
    
    def __init__(self):
        self.protocol = None
    
    def execute(self, protocol, line=''):
        self.protocol = protocol
    
    def set_command(self, protocol, cmd):
        protocol.command = globals()[cmd+'Command']()
        
    def write_data(self, transport, filename):
        self.pathManager = path.FileManager(filename)
        self.pathManager.write_data_to_transport(transport)
        self.send_command(transport, COMMANDS['SYNC_RESPONSE_FINISH'])
        self.pathManager.write_file_info_to_transport(transport)
        
#    def send_command(self, transport, cmd):
#        transport.write(CMD_BEGIN + cmd + CMD_END)
    
class PullRequestCommand(Command):
    def __init__(self):
        self.pathManager = path.DirManager(path.PathManager.source_dir)
    
    def execute(self, protocol, line=''):
        Command.execute(self, line)
        '''send file and folder name to the client'''
        logging.debug(self.__class__)
        transport = protocol.transport
        self.pathManager.send_pathname_to_transport(self.pathManager.source_dir, transport)
        
class PullResponseCommand(Command):
    '''execute in client'''
    def execute(self, protocol, line=''):
        Command.execute(self, line)
        logging.debug(self.__class__)
        if not line ==  path.PathManager.source_dir:
            pathname = os.path.join(path.PathManager.source_dir, line)
            if os.path.exists(pathname):
                if os.path.isfile(pathname):
                    self.send_command(protocol.transport, COMMANDS['FILE_INFO_REQUEST'] + line)
            else:
                self.send_command(protocol.transport, COMMANDS['SYNC_REQUEST'] + line)
        
class SyncRequestCommand(Command):
    def __init__(self):
        self.pathManager = path.PathManager()
    
    def execute(self, protocol, line=''):
        Command.execute(self, line)
        logging.debug(self.__class__)
        self.sync_response(protocol.transport, line)
        
    def sync_response(self, transport, line=''):
        if not line == '':
            pathname = os.path.join(path.PathManager.source_dir, line)
            if os.path.isfile(pathname):
                logging.debug("SYNC_RESPONSE_FILE%s" % line)
                self.send_command(transport, COMMANDS['SYNC_RESPONSE_FILE'] + line)
                self.write_data(transport, pathname)
            elif os.path.isdir(pathname):
                logging.debug("SYNC_RESPONSE_DIR%s" % line)
                self.send_command(transport, COMMANDS['SYNC_RESPONSE_DIR'] + line)
        
class SyncResponseFileCommand(Command):
    def execute(self, protocol, line=''):
        Command.execute(self, line)
        logging.debug(self.__class__)
        protocol.current_file = line
        
class SyncResponseDirCommand(Command):
    '''make directories that not exist in client firstly'''
    def __init__(self):
        self.pathManager = path.PathManager()
    
    def execute(self, protocol, line=''):
        Command.execute(self, line)
        logging.debug(self.__class__)
        pathname = os.path.join(self.pathManager.source_dir, line)
        self.pathManager = path.DirManager(pathname)
        if not line == '':
            self.pathManager.make()

class SyncResponseFinishCommand(Command):
    def execute(self, protocol, line=''):
        Command.execute(self, line)
        logging.debug(self.__class__)
        self.pathManager = path.FileManager(protocol.current_file)
        self.pathManager.db_update_file_info()
        print self.pathManager.get_last_synced()
        protocol.current_file = ""
        
class FileInfoRequestCommand(Command):
    def execute(self, protocol, line=''):
        Command.execute(self, line)
        logging.debug(self.__class__)
        pathname = os.path.join(path.PathManager.source_dir, line)
        self.pathManager = path.FileManager(pathname)
        self.pathManager.write_file_info_to_transport(protocol.transport)
        
class FileInfoConfirmCommand(Command):
    '''md5 check process: to confirm we receive file correctly'''
    def execute(self, protocol, line=''):
        Command.execute(self, line)
        logging.debug(self.__class__)
        file_info_remote = ast.literal_eval(line)
        pathname = os.path.join(path.PathManager.source_dir, file_info_remote['filename'])
        self.pathManager = path.FileManager(pathname)
        if not file_info_remote['md5'] == self.pathManager.get_md5():
            '''if md5 of two files are not the same, we should transform the file again'''
            self.pathManager.delete()
            self.send_command(protocol.transport, COMMANDS['SYNC_REQUEST'] + file_info_remote['filename'])
        else:
            self.pathManager.db_update_file()
            
class FileInfoResponseCommand(Command):
    '''files with the same name were in both side, but theirs contents are not the same.'''
    def execute(self, protocol, line=''):
        Command.execute(self, line)
        logging.debug(self.__class__)
        file_info_remote = ast.literal_eval(line)
        pathname = os.path.join(path.PathManager.source_dir, file_info_remote['filename'])
        self.pathManager = path.FileManager(pathname)
        if not file_info_remote['md5'] == self.pathManager.get_md5():
            '''md5 are not the same, we should firstly decide whether this file in client is in use.
            if it is,  do not sync this file. Secondly, we should compare the modified time with the sync time
            of this file in both sides, if the modified times in both sides are older than sync time,
            do not sync this file, else, send the file from the end which has a newer modified time to the end in which 
            the modified time is older.
            '''
            if file_info_remote['last_modified'] < file_info_remote['last_synced'] and \
                self.pathManager.get_last_modified() < file_info_remote['last_synced']:
                    '''file conclict'''
            else:
                if file_info_remote['last_modified'] < self.pathManager.get_last_modified:
                    '''send local file to remote'''
                    self.send_command(protocol.transport, COMMANDS['SYNC_RESPONSE_FILE'] + file_info_remote['filename'])
                    self.write_data(protocol.transport, pathname)
                elif file_info_remote['last_modified'] > self.pathManager.get_last_modified:
                    '''send a request to receive  remote file'''
                    self.send_command(protocol.transport, COMMANDS['SYNC_REQUEST'] + file_info_remote['filename'])
        else:
            self.pathManager.db_update_file()