import os

import mysql.connector as database

username = "doadmin"

password = "AVNS_Tl4BP3iZ00Ikk8Ix8DQ"

host_db = "mysqldb-weerwijzer-do-user-15988447-0.c.db.ondigitalocean.com"

port = "25060"

db = "defaultdb"

sslmode = "REQUIRED"


# db = os.environ.get("db")

connection = database.connect(
    user=username,
    password=password,
    host=host_db,
    port=port,
    database=db,)

# Create a cursor
cursor = connection.cursor() 

# Define the table creation SQL 
# querycreate_table_query = ''' 
#     CREATE TABLE IF NOT EXISTS weerwijzertable (     
#         id INT AUTO_INCREMENT PRIMARY KEY,     
#         winddirection VARCHAR(255),     
#         degrees INT,     
#         currentdate DATE ); '''

# Execute the query to create the table
# cursor.execute(querycreate_table_query) 
# Commit the changes
# connection.commit()
 # Close the cursor and connectionc
# cursor.close() 
# connection.close()

querycreate_table_query = '''
insert INTO weerwijzertable (winddirection,degrees,currentdate) VALUES ('S', 36, '2022-10-10');
'''
# print(querycreate_table_query)

cursor.execute(querycreate_table_query) 
connection.commit()



# Create a cursorcursor = connection.cursor() # Replace 'your_table_name' with the actual table name
table_name = 'weerwijzertable'# Define the SELECT query to fetch all rows from the table
select_query = f'SELECT * FROM {table_name};'
# Execute the query
cursor.execute(select_query) # Fetch all rows
result = cursor.fetchall() # Print the table 
header = [desc[0] for desc in cursor.description]
# print("\t".join(header)) # Print each row
for row in result:     
    print("\t".join(map(str, row))) 
# Close the cursor and connection
cursor.close() 
connection.close()