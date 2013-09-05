import os
import stat

SOURCE_DIR = "D:\\to_client"

class File(object):
    def __init__(self, filename):
        self.filename = filename
        self.md5 = None
        self.lastSynced = None
        self.pathname = os.path.join(SOURCE_DIR, filename)
        fileStats = os.stat(self.pathname)
        self.fileSize = fileStats[stat.ST_SIZE]
        self.lastModified = fileStats[stat.ST_MTIME]
        self.lastAccessed = fileStats[stat.ST_ATIME]
        self.creationTime = fileStats[stat.ST_CTIME]
        self.fileMode = fileStats[stat.ST_MODE]

class FileProxy(object):
    def __init__(self, filename):
        self.pathname = os.path.join(SOURCE_DIR, filename)
    
    def open_file(self, mod):
        return open(self.pathname, mod)

    def make_dir(self):
        os.path.exists(self.pathname) or os.mkdir(self.pathname) 