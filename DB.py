# Description: This script establishes a connection to a MySQL database and performs the following operations:
from dotenv import load_dotenv
import mysql.connector as database
import os


# Database connection parameters
load_dotenv()
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

def create_table(cursor):
    """
    Creates a table if it doesn't exist in the database.
    """
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS weerwijzertable (     
        id INT AUTO_INCREMENT PRIMARY KEY,     
        winddirection VARCHAR(255),     
        degrees INT,     
        currentdate DATE
    );
    '''
    try:
        cursor.execute(create_table_query)
        print("Table 'weerwijzertable' created successfully.")
    except database.Error as e:
        print(f"Error creating table: {e}")

def insert_data(cursor, connection):
    """
    Inserts sample data into the table.
    """
    insert_query = '''
    INSERT INTO weerwijzertable (winddirection, degrees, currentdate) 
    VALUES ('S', 36, '2022-10-10');
    '''
    try:
        cursor.execute(insert_query)
        connection.commit()
        print("Data inserted successfully.")
    except database.Error as e:
        print(f"Error inserting data: {e}")
        connection.rollback()

def fetch_data(cursor):
    """
    Fetches all rows from the table and prints them.
    """
    table_name = 'weerwijzertable'
    select_query = f'SELECT * FROM {table_name};'
    try:
        cursor.execute(select_query)
        result = cursor.fetchall()
        header = [desc[0] for desc in cursor.description]
        print("\t".join(header))
        for row in result:
            print("\t".join(map(str, row)))
    except database.Error as e:
        print(f"Error fetching data: {e}")

def main():
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            create_table(cursor)
            insert_data(cursor, connection)
            fetch_data(cursor)
        finally:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    main()
