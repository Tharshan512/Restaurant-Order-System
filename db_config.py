import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="User2002",
        database="restaurant_db"
    )
    return connection