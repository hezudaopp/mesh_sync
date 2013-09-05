import os
import exceptions
import logging
import command
import files
import db
import time
from hashlib import md5

class PathManager(object):
    source_dir = 'to_client'
    source_dir_len = len(source_dir)+1
    buf_size = 128 * 1024
    
    def __init__(self, pathname = source_dir):
        '''self.pathname includes source_dir path'''
        self.pathname = pathname
        
    def delete(self):
        pass
    
class FileManager(PathManager):
    def __init__(self, pathname = PathManager.source_dir):
        PathManager.__init__(self, pathname)
        self.db = db.Db()
        self.file = files.File(pathname[self.source_dir_len:])
        self.file.lastSynced = self.db_get_last_synced()
        self.file.md5 = self._generate_md5()
        self.file_info = {'filename':self.file.filename, 'md5':self.file.md5, 
                          'last_modified':self.file.lastModified, 'size':self.file.fileSize, 
                          'last_accessed':self.file.lastAccessed, 'last_synced':self.file.lastSynced}
        
    def delete(self):
        '''delete a file'''
        try:
            os.remove(self.pathname)
        except:
            print "os.remove in FileManager.delete" 
    
    def write_file(self, data):
        '''save file'''
        print 'write file size:', len(data), ' filename:', self.pathname
        '''On Windows, 'b' appended to the mode opens the file in binary mode'''
        fp = open(self.pathname, "ab+")
        fp.write(data)
        fp.close()
        
    def write_data_to_transport(self, transport):
        transport.write(command.FILE_BEGIN)
        try:
            fp = open(self.pathname,'rb')
            while 1:
                filedata = fp.read(self.buf_size)
                if not filedata: break
                else:
                    transport.write(filedata)
            fp.close()
        except exceptions.IOError:
            logging.error("file IO error, filename: %s" % self.pathname)
        transport.write(command.FILE_END)
        
    def write_file_info_to_transport(self, transport):
        self.file_info['filename'] = self.file.filename
        self.file_info['last_synced'] = self.file.db_get_last_synced(self.file_info['filename'])
        transport.write(command.CMD_BEGIN)
        transport.write(command.COMMANDS['FILE_INFO_RESPONSE'] + str(self.file_info))
        transport.write(command.CMD_END)
        
    def is_exists(self):
        return os.path.isfile(self.file.filename)
        
    def db_get_file(self):
        sqlStr = "SELECT * FROM files WHERE filename = ? limit 1"
        args = (self.file.filename, )
        row = self.db.do_query(sqlStr, args)
        if row == None:
            return None
        else:
            self._set_file(row[0])
            return self.file 
        
    def db_insert_file(self):
        self.lastSynced = time.time()
        if not self._db_is_exist():
            sqlStr = "INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            args = (self.file.filename, self.file.md5, self.file.lastSynced, self.file.fileSize, \
                    self.file.lastModified, self.file.lastAccessed, self.file.creationTime, self.file.fileMode)
            self.db.do_query(sqlStr, args)
        else:
            pass
#            self.db_update_file()
        
    def _db_is_exist(self):
        sqlStr = "SELECT filename from files where filename = ?"
        args = (self.file.filename,)
        row = self.db.do_query(sqlStr, args)
        if not row == None: return True
        else: return False
        
    def db_update_file(self):
        self.file.lastSynced = time.time()
        sqlStr = "UPDATE files SET md5 = ?, last_synced = ?, file_size = ?, last_modified = ?, \
        last_accessed = ?, creation_time = ?, file_mod = ? WHERE filename = ?"
        args = (self.file.md5, self.file.lastSynced, self.file.fileSize, self.file.lastModified, \
                self.file.lastAccessed, self.file.creationTime, self.file.fileMode, self.file.filename)
        self.db.do_query(sqlStr, args)
    
    def db_get_last_synced(self):
        sqlStr = "SELECT last_synced FROM files WHERE filename = ? limit 1"
        args =(self.file.filename,)
        row = self.db.do_query(sqlStr, args)
        if not row == None:
            return row
    
    def db_get_md5(self):
        sqlStr = "SELECT md5 FROM files WHERE filename = ? limit 1"
        args =(self.file.filename,)
        row = self.db.do_query(sqlStr, args)
        return row[0]
    
    def _generate_md5(self):
        '''generate md5 value of a given file'''
        m = md5()
        fd = open(self.pathname, 'rb')    # open the file in binary mode
        m.update(fd.read())
        fd.close()
        return m.hexdigest()
            
    def _set_file(self, row):
        self.file.filename = row[0]
        self.file.md5 = row[1]
        self.file.lastSynced = row[2]
        self.file.fileSize = row[3]
        self.file.lastModified = row[4]
        self.file.lastAccessed = row[5]
        self.file.creationTime = row[6]
        self.file.fileMode = row[7]
    
    def get_last_synced(self):
        return self.file_info['last_synced']
    
    def get_last_modified(self):
        return self.file_info['last_modified']
    
    def get_filename(self):
        return self.file_info['filename']
    
    def get_filesize(self):
        return self.file_info['size']
    
    def get_md5(self):
        return self.file_info['md5']
    
class DirManager(PathManager):
    def __init__(self, dirname = PathManager.source_dir):
        PathManager.__init__(self, dirname)
        self.dirname = dirname[self.source_dir_len:]
        self.pathManager = None
        
    def db_init(self):
        self.db_insert_files(self.source_dir)
    
    def db_insert_files(self, pathname):
        for handle_request in os.listdir(pathname):
            sourceF = os.path.join(pathname, handle_request)
            if os.path.isfile(sourceF):
                self.pathManager = FileManager(sourceF)
                self.pathManager.db_insert_file()
            elif os.path.isdir(sourceF):
                self.db_insert_files(sourceF)
        
    def delete(self):
        for item in os.listdir(self.pathname):
            itemsrc = os.path.join(self.pathname, item)
            if os.path.isfile(itemsrc):
                self.pathManager = FileManager(itemsrc)
                self.pathManager.delete()
            else:
                try:
                    os.rmdir(itemsrc)
                except:
                    print "os.rmdir in DirManager.delete"

    def make(self):
        if not os.path.isdir(self.pathname):
            os.mkdir(self.pathname)
            
    def clean(self, src):
        '''delete files and folders recursively and then make a new dir with the same name'''
        self.delete(src)
        os.mkdir(src)
        
    def send_pathname_to_transport(self, pathname, transport):
        for handle_request in os.listdir(pathname):
            sourceF = os.path.join(pathname, handle_request)
            if os.path.isfile(sourceF) or os.path.isdir(sourceF):
                logging.info('send pathname %s to %s' % (self.source_dir_len, transport.getPeer().host))
                transport.write(command.CMD_BEGIN + command.COMMANDS['PULL_RESPONSE'] + sourceF[self.source_dir_len:] + command.CMD_END)
                if os.path.isdir(sourceF):
                    self.send_pathname_to_transport(sourceF, transport)
