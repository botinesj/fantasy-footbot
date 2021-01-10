import mysql.connector as mysql
from config import PASSWORD

mydb = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = PASSWORD,
    database = "users"
)

mycursor = mydb.cursor()

