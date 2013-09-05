import os
import stat
import path

class File(object):
    def __init__(self, pathname):
        self.filename = pathname
        self.md5 = None
        self.lastSynced = None
        self.pathname = os.path.join(path.PathManager.source_dir, pathname)
        fileStats = os.stat(self.pathname)
        self.fileSize = fileStats[stat.ST_SIZE]
        self.lastModified = fileStats[stat.ST_MTIME]
        self.lastAccessed = fileStats[stat.ST_ATIME]
        self.creationTime = fileStats[stat.ST_CTIME]
        self.fileMode = fileStats[stat.ST_MODE]
