import os
import sqlite3
from sqlite3 import Error, Connection
from typing import List
from .model import FillDB

sql_create_fills_table =    """ CREATE TABLE IF NOT EXISTS fills (
                                        id integer PRIMARY KEY,
                                        symbol text NOT NULL,
                                        date text NOT NULL,
                                        country text NOT NULL,
                                        strategy text NOT NULL
                                    ); """

def create_connection(path, fileName):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        modpath = os.path.abspath(path)
        datapath = os.path.join(modpath, fileName)
        conn = sqlite3.connect(datapath)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

class DatabaseModule:
    conn: Connection

    def getFills(self) -> List[FillDB]:
        """
        Query all rows in the fills table
        :param conn: the Connection object
        :return:
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM fills")

        rows = cur.fetchall()
        fills = []

        for row in rows:
            fills.append(FillDB.init_from_db(row))
        
        return fills

    def createFill(self, fill: FillDB) -> int:
        """
        Create a new fill into the Fills table
        :param conn:
        :param fill:
        :return: fill id
        """

        sql = ''' INSERT INTO fills(symbol,date,country,strategy)
                    VALUES(?,?,?,?) '''
        cur = self.conn.cursor()
        cur.execute(sql, fill.sqlFormat)
        self.conn.commit()
        return cur.lastrowid

    def deleteFills(self, fills: List[FillDB]):
        """
        Delete fills
        :param conn:  Connection to the SQLite database
        :param fills: list of fills to delete
        :return:
        """
        for fill in fills:
            sql = 'DELETE FROM fills WHERE (symbol=? AND date=? AND country=? AND strategy=?)'
            cur = self.conn.cursor()
            cur.execute(sql, (fill.symbol, fill.dateToString, fill.country.code, fill.strategy.value))
            self.conn.commit()

    def openDatabaseConnection(self):
        self.conn = create_connection('database/sqlite/db', 'tiopatinhas.db')
        if self.conn is not None:
            # create projects table
            create_table(self.conn, sql_create_fills_table)
        else:
            print("Error! cannot create the database connection.")

    def openDatabaseConnectionForBacktest(self):
        self.conn = create_connection('database/sqlite/db', 'backtest.db')
        if self.conn is not None:
            # create projects table
            create_table(self.conn, sql_create_fills_table)
        else:
            print("Error! cannot create the database connection.")

    def closeDatabaseConnection(self):
        self.conn.close()