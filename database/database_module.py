import sys, os
import sqlite3
from sqlite3 import Error, Connection, Cursor
from datetime import date, datetime, timedelta
from .model import FillDB

sql_create_fills_table =    """ CREATE TABLE IF NOT EXISTS fills (
                                        id integer PRIMARY KEY,
                                        symbol text NOT NULL,
                                        date text NOT NULL
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

    def getFills(self) -> [FillDB]:
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

        sql = ''' INSERT INTO fills(symbol,date)
                    VALUES(?,?) '''
        cur = self.conn.cursor()
        cur.execute(sql, fill.sqlFormat)
        self.conn.commit()
        return cur.lastrowid

    def deleteFills(self, fills: [FillDB]):
        """
        Delete fills
        :param conn:  Connection to the SQLite database
        :param fills: list of fills to delete
        :return:
        """
        for fill in fills:
            sql = 'DELETE FROM fills WHERE (symbol=? AND date=?)'
            cur = self.conn.cursor()
            cur.execute(sql, (fill.symbol, fill.dateToString))
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

if __name__ == '__main__':
    databaseModule = DatabaseModule()
    databaseModule.openDatabaseConnection()
    # fill = FillDB("AAPL", date(2021, 4, 5))
    # fill_id = databaseModule.createFill(fill)

    # fill = FillDB("AAPL", date(2020, 12, 5))
    # fill_id = databaseModule.createFill(fill)

    # fill = FillDB("AAPL", date(2021, 3, 5))
    # fill_id = databaseModule.createFill(fill)

    # fill = FillDB("AAPL", date(2020, 7, 5))
    # fill_id = databaseModule.createFill(fill)

    # fill = FillDB("AAPL", date(2021, 1, 5))
    # fill_id = databaseModule.createFill(fill)

    # fill = FillDB("AAPL", date(2020, 9, 5))
    # fill_id = databaseModule.createFill(fill)

    # fill = FillDB("AAPL", date(2020, 11, 5))
    # fill_id = databaseModule.createFill(fill)

    # fill = FillDB("AAPL", date(2020, 10, 5))
    # fill_id = databaseModule.createFill(fill)

    # fill = FillDB("AAPL", date(2020, 8, 5))
    # fill_id = databaseModule.createFill(fill)

    # fill = FillDB("AAPL", date(2021, 2, 5))
    # fill_id = databaseModule.createFill(fill)


    fills = databaseModule.getFills()
    for fill in fills:
        print(fill.date)
    
    limitDate = date.today()-timedelta(days=40)
    print("-------", limitDate)
    filteredFills = list(filter(lambda x: x.date < limitDate, fills))
    filteredFills.sort(key=lambda x: x.date, reverse=True)
    for fill in filteredFills:
        print(fill.date)

    # print("Removing")
    # databaseModule.deleteFills(filteredFills)
    # fills = databaseModule.getFills()
    # print("List new fills")
    # for fill in fills:
    #     print(fill.date)
