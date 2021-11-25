import sqlite3
import pandas as pd

class db:

    def __init__(self, dbFileName: str):
        self.dbFileName = dbFileName

        # This connects to an existing database or creates it if it doesn't exists
        #self.conn = sqlite3.connect(self.dbFileName)

        self.createDatabaseStructureIfNotExists()


    # This function creates the database and the tables if they don't exist
    def createDatabaseStructureIfNotExists(self):

        try:

            # Connecting to sqlite3 .file
            conn = sqlite3.connect(self.dbFileName)

            # Creating a cursor object using the cursor() method
            cursor = conn.cursor()

            # Creating table as per requirement
            sql = """
                CREATE TABLE IF NOT EXISTS 'dimChains' (
                    'id'	            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    'description'	    TEXT NOT NULL UNIQUE,
                    'isActive'	        boolean NOT NULL DEFAULT 0,
                    'insertDatetime'	datetime DEFAULT current_timestamp
                );
            """

            cursor.execute(sql)

            sql = """
                CREATE TABLE IF NOT EXISTS 'dimTypes' (
                    'id'	            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    'description'	    TEXT NOT NULL UNIQUE,
                    'insertDatetime'	datetime DEFAULT current_timestamp
                );
            """

            cursor.execute(sql)

            sql = """
                CREATE TABLE IF NOT EXISTS 'dimCryptos' (
                    'id'	            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    'symbol'	        TEXT,
                    'symbolName'      TEXT,
                    'slug'            TEXT,
                    'contract'	    TEXT NOT NULL UNIQUE,
                    'FK_typeId'	    INTEGER,
                    'FK_chainId'	    INTEGER,
                    'insertDatetime'	datetime DEFAULT current_timestamp,
                    FOREIGN KEY('FK_typeId')  REFERENCES dimTypes('id'),
                    FOREIGN KEY('FK_chainId') REFERENCES dimChains('id')
                );
            """

            cursor.execute(sql)

            sql = """
                CREATE TABLE IF NOT EXISTS tradingHistory (
                    'id'	                INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    'FK_cryptoId'	        INTEGER NOT NULL,
                    'isSold'	            boolean NOT NULL DEFAULT 0,
                    'isTrading'	            boolean NOT NULL DEFAULT 0,
                    'prevPrice'	            numeric,
                    'price'	                numeric,
                    'sellPrice'	            numeric,
                    'percentageDiff'	    numeric,
                    'sellPercentageDiff'	numeric,
                    'buyDatetime'	        datetime,
                    'sellDatetime'	        datetime,
                    'realBuyPrice'	        numeric,
                    'realSellPrice'	        numeric,
                    'buyURL'	            TEXT,
                    'approveSellURL'	    TEXT,
                    'sellURL'	            TEXT,
                    FOREIGN KEY('FK_cryptoId') REFERENCES dimCryptos('id')
                );
            """

            cursor.execute(sql)

            # Commit your changes in the database
            conn.commit()

        except Exception as e:
            print(e)
            exit()

        # Closing the connection
        conn.close()


    # Return pandas dataFrame by given query
    def getDataframe(self, sql):

        # Open connection
        conn = sqlite3.connect(self.dbFileName)

        # Get data
        cursor = conn.execute(sql)

        # Get column names in order
        columnNames = list(map(lambda x: x[0], cursor.description))

        # Close conn
        conn.close()

        # Return pandas dataFrame
        return pd.DataFrame(cursor.fetchall(), columns=columnNames)





ob = db(dbFileName='test.db')

        
print(ob.getDataframe(sql="SELECT * FROM dimChains WHERE isActive = 1"))