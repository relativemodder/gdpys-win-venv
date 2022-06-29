from typing import Any
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.cursor import CursorBase
import mysql.connector

class Database:
    host: str = "localhost"
    user: str = "root"
    password: str = ""
    db_name: str = "gdpys"
    connection: MySQLConnectionAbstract
    cursor: CursorBase

    def __init__(self, assoc=False):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            passwd=self.password,
            database=self.db_name
        )
        self.cursor = self.connection.cursor(dictionary=assoc)
    def close(self):
        self.connection.close()
        
