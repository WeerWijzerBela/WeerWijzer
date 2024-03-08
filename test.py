import DB

def insert_data(cursor):
    """
    Inserts data into the database.
    """
    insert_query = '''
    INSERT INTO locaties (locatie) VALUES ('Maastricht');
    '''
    try:
        cursor.execute(insert_query)
        print("Data inserted successfully.")
    except DB.database.Error as e:
        print(f"Error inserting data: {e}")



def main():
    print("Hello, World!")
    connection = DB.connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            # insert_data(cursor)
        finally:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    main()
