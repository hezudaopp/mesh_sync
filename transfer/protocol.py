from twisted.internet import protocol
import logging

import command
import path

class MeshProtocol(protocol.Protocol):
    
    def __init__(self):
        self.command = command.Command()
        self.pathManager = None 
        self.pathname = ""
        self.current_file = ""
        self.is_found_file_end = True
    
    def dataReceived(self, line):
        self.line = line
        while len(self.line) > 0:
            '''retrieve command'''
            if self.is_found_file_end:
                '''we should ensure that the entire file should be received 
                correctly before retrieving command, so we will not miss any data
                '''
                cmd = self.retrieve_command()
                if cmd:
                    logging.debug("%s cmd: %s" % (self.__class__, cmd))
                    self.process_cmd(cmd)
            if len(self.line) > 0 and not self.current_file == "":
                '''retrieve file data, write data to local file using the same name'''
                data = self.retrieve_data()
                self.pathManager = path.FileManager(self.current_file)
                self.pathManager.write_file(data)
            else:
                logging.debug("no file data receive or file not prepared")
 
    def retrieve_command(self):
        '''retrieve command from receive buffer'''
        index1 = self.line.find(command.CMD_BEGIN)
        index2 = self.line.find(command.CMD_END)
        if index1 >= 0 and index2 >= 0:
            '''retrieve command line, line will be retrieved 
            only when ${command.CMD_BEGIN} and ${command.CMD_END} commands found
            '''
            cmd = self.line[index1+len(command.CMD_BEGIN):index2]
            self.line = self.line[index2+len(command.CMD_END):]
            return cmd
        else:
            return None
        
    def retrieve_data(self):
        '''retrieve data from receive buffer'''
        data = ""
        if not self.is_found_file_end:
            end_index = self.line.find(command.FILE_END)
            if end_index >= 0:
                '''find the end tag of a file
                append the data to the data received in pre transport buffer(s)
                '''
                data = self.line[:end_index]
                self.line = self.line[end_index+len(command.FILE_END):]
                self.is_found_file_end = True
            else:
                '''all data in transport buffer is file data, not any self defined tag'''
                data = self.line
                self.line = ""
        else:
            begin_index = self.line.find(command.FILE_BEGIN)
            end_index = self.line.find(command.FILE_END)
            if begin_index >= 0 and end_index >= 0:
                '''the entire file is in one transport buffer'''
                data = self.line[begin_index+len(command.FILE_BEGIN):end_index]
                self.line = self.line[end_index+len(command.FILE_END):]
            elif begin_index >= 0:
                '''if a file is bigger enough (bigger than the transport buffer),
                this file would be tranported in several transports buffer.
                we should set ${self.is_found_file_end} false, so next time we receive the transport buffer,
                we will firstly retrieve data other than command'''
                data = self.line[begin_index+len(command.FILE_BEGIN):]
                self.line = ""
                self.is_found_file_end = False
        return data
        
    def process_cmd(self, cmd):
        '''implements using command pattern'''
        for cmd_str in command.COMMANDS.values():
            if cmd.startswith(cmd_str):
                lens = len(cmd_str)
                self.pathname = cmd[lens:]
                cmd = cmd[0:lens]
                self.command.set_command(self, cmd)
                self.command.execute(self, self.pathname)
                return