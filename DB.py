# Description: This script establishes a connection to a MySQL database and performs the following operations:
import mysql.connector as database
import os
import dotenv

dotenv.load_dotenv()
# Database connection parameters
username = os.environ.get("DB_USER")
password = os.environ.get("DB_PASSWORD")
host_db = os.environ.get("DB_HOST")
port = os.environ.get("DB_PORT")
db = os.environ.get("DB_NAME")

if None in (username, password, host_db, port, db):
    raise ValueError("One or more environment variables are not set.")


config = {
    'user': os.environ.get("DB_USER"),
    'password': os.environ.get("DB_PASSWORD"),
    'host': os.environ.get("DB_HOST"),
    'port': os.environ.get("DB_PORT"),
    'database': os.environ.get("DB_NAME"),
}

def connect_to_database():
    """
    Establishes a connection to the MySQL database.
    """
    try:
        connection = database.connect(**config)
        return connection
    except database.Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def create_table_locaties(cursor):
    """
    Creates a table if it doesn't exist in the database.
    """
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS Locaties (     
        locatieId INT AUTO_INCREMENT PRIMARY KEY,     
        locatie VARCHAR(255),
    );
    '''
    try:
        cursor.execute(create_table_query)
        print("Table 'Locatie' created successfully.")
    except database.Error as e:
        print(f"Error creating table: {e}")

def create_table_voorspellingen(cursor):
    """
    Creates a table if it doesn't exist in the database.
    """
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS voorspellingen (     
        voorspellingId INT AUTO_INCREMENT PRIMARY KEY,     
        locatieId INT,
        datetime DATETIME,
        currenttemp Decimal(5,2),
        zWaarde INT,
        FOREIGN KEY (locatieId) REFERENCES Locaties(locatieId)
    );
    '''
    try:
        cursor.execute(create_table_query)
        print("Table 'voorspellingen' created successfully.")
    except database.Error as e:
        print(f"Error creating table: {e}")

def create_table_voorspellinguren(cursor):
    """
    Creates a table if it doesn't exist in the database.
    """
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS voorspellinguren (     
        voorspellingUrenId INT AUTO_INCREMENT PRIMARY KEY,     
        voorspellingId INT,
        datetime DATETIME,
        temperature Decimal(5,2),
        zWaarde INT,
        FOREIGN KEY (voorspellingId) REFERENCES voorspellingen(voorspellingId)
    );
    '''
    try:
        cursor.execute(create_table_query)
        print("Table 'weervoorspellingen' created successfully.")
    except database.Error as e:
        print(f"Error creating table: {e}")

def create_table_metingen(cursor):
    """
    Creates a table if it doesn't exist in the database.
    """
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS metingen (     
        metingenId INT AUTO_INCREMENT PRIMARY KEY,     
        locatieId INT,
        datetime DATETIME,
        currenttemp Decimal(5,2),
        pressure Decimal(5,2),
        winddirection VARCHAR(255),
        FOREIGN KEY (locatieId) REFERENCES Locaties(locatieId)
    );
    '''
    try:
        cursor.execute(create_table_query)
        print("Table 'metingen' created successfully.")
    except database.Error as e:
        print(f"Error creating table: {e}")

def create_table_metingenuren(cursor):
    """
    Creates a table if it doesn't exist in the database.
    """
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS metinguren (     
        metingUrenId INT AUTO_INCREMENT PRIMARY KEY,     
        metingenId INT,
        datetime DATETIME,
        Temperature Decimal(5,2),
        pressure Decimal(5,2),
        winddirection VARCHAR(255),
        FOREIGN KEY (metingenId) REFERENCES metingen(metingenId)
    );
    '''
    try:
        cursor.execute(create_table_query)
        print("Table 'metinguren' created successfully.")
    except database.Error as e:
        print(f"Error creating table: {e}")

def main():
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            create_table_locaties(cursor)
            create_table_voorspellingen(cursor)
            create_table_metingen(cursor)
            create_table_metingenuren(cursor)
        finally:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    main()
