import sqlite3

class Db(object):
    db_name = "mesh.db"
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.row = None
        self.sqlStr = ""

    def _open_connection(self):
        self.connection = sqlite3.connect(self.db_name)
        
    def _commit(self):
        self.connection.commit()
        
    def _close_connection(self):
        self.connection.close()
        
    def _execute_query(self, args):
        self._open_connection()
        self.cursor = self.connection.cursor()
        self.cursor.execute(self.sqlStr, args)
        self.row = self.cursor.fetchall()
        self._commit()
        self._close_connection()
        
    def do_query(self, sqlStr, args = ()):
        self.sqlStr = sqlStr
        self._execute_query(args)
        return self.row
    
    def create_tables(self):
        sqlStr = "CREATE TABLE IF NOT EXISTS files(filename NVARCHAR(255), md5 CHAR(32), last_synced INTEGER, \
        file_size INTEGER, last_modified INTEGER, last_accessed INTEGER, creation_time INTEGER, file_mod NVARCHAR(24))"
        self.do_query(sqlStr)
