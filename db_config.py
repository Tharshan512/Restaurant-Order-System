import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="5890Qudsia!",
        database="restaurant_db"
    )
    return connection