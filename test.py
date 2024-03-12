import DB
from datetime import date

def insert_data(cursor):
    """
    Inserts data into the database.
    """
    insert_query = '''
    INSERT INTO locaties (locatie) VALUES ('Apeldoorn');
    '''
    try:
        cursor.execute(insert_query)
        print("Data inserted successfully.")
    except DB.database.Error as e:
        print(f"Error inserting data: {e}")



def main():
    
    connection = DB.connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            insert_data(cursor)
            connection.commit()
        finally:
            cursor.close()
            connection.close()


print(date.today())
print("Hello, World!")
