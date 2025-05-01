import pymysql

def create_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='sqladmin',
        database='meal_base',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection
