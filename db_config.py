import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kartikay.25",
        database="restaurant_db"
    )
    return connection