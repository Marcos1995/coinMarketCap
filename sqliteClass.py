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

        # Creating table as per requirement
        query = """
            CREATE TABLE IF NOT EXISTS 'dimChains' (
                'id'	            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                'description'	    TEXT NOT NULL UNIQUE,
                'isActive'	        boolean NOT NULL DEFAULT 0,
                'insertDatetime'	datetime DEFAULT current_timestamp
            );
        """

        self.executeQuery(query)

        query = """
            CREATE TABLE IF NOT EXISTS 'dimTypes' (
                'id'	            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                'description'	    TEXT NOT NULL UNIQUE,
                'insertDatetime'	datetime DEFAULT current_timestamp
            );
        """

        self.executeQuery(query)

        query = """
            CREATE TABLE IF NOT EXISTS 'dimCryptos' (
                'id'	            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                'symbol'	        TEXT,
                'symbolName'        TEXT,
                'slug'              TEXT,
                'contract'	        TEXT NOT NULL UNIQUE,
                'FK_typeId'	        INTEGER,
                'FK_chainId'	    INTEGER,
                'insertDatetime'	datetime DEFAULT current_timestamp,
                FOREIGN KEY('FK_typeId')  REFERENCES dimTypes('id'),
                FOREIGN KEY('FK_chainId') REFERENCES dimChains('id')
            );
        """

        self.executeQuery(query)

        query = """
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

        self.executeQuery(query)


    # Prepare the pandas DataFrame data to be inserted in a table
    def prepareInsertInto(self, sourceDf=None, targetTable:str=None):

        # Validations
        if sourceDf is None:
            return

        print(sourceDf)

        values = ""

        # Prepare column names to be inserted
        columnNames = "'" + "', '".join(list(sourceDf)) + "'"

        # For each row, concatenate the values to prepare the INSERT INTO statement
        for i in range(len(sourceDf)):

            # Split with "," the values to be inserted (mandatory)
            if i > 0:
                values += ", "

            # Concatenate values to be inserted from each row
            rowValues = sourceDf.iloc[i,:].apply(str).values
            values += "('" + "', '".join(rowValues) + "')"

        # Create query statement
        query = f"""
                INSERT INTO {targetTable} ({columnNames})
                VALUES {values};
            """

        self.executeQuery(query)


    # Execute any query
    def executeQuery(self, query:str=None):
        
        # Validation
        if query is None:
            return

        print(query)

        # Verify and assign which type of query is it, commit or not commit one
        searchfor = ["SELECT"]
        isToCommitTransaction = any(command not in query for command in searchfor)

        try:

            # Open connection
            conn = sqlite3.connect(self.dbFileName)

            # INSERT, UPDATE or DELETE statements
            if isToCommitTransaction:

                # Create cursor
                cursor = conn.cursor()

                # Execute query
                cursor.execute(query)

                # Commit transaction
                conn.commit()
            
            else: # SELECT statement, returns pandas DataFrame

                # Execute query
                cursor = conn.execute(query)

                # Fetch all data
                data = cursor.fetchall()

                # Get column names in order
                columnNames = list(map(lambda x: x[0], cursor.description))

            # Close conn
            conn.close()

            # If we executed a SELECT statement, return a formatted pandas dataFrame
            if not isToCommitTransaction:
                return pd.DataFrame(data, columns=columnNames)

        except Exception as e:
            print(e)
            exit()




ob = db(dbFileName='test.sqlite')
df = ob.executeQuery(query="SELECT 'test4' as description, 0 as isActive")
ob.prepareInsertInto(sourceDf=df, targetTable="dimChains")