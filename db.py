
import mysql.connector as mysql

import mysql.connector as mysql
from config import PASSWORD

mydb = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = PASSWORD,
    database = "users"
)

mycursor = mydb.cursor()

#mycursor.execute("CREATE TABLE Users (userID bigint PRIMARY KEY, team_name "
#                 "VARCHAR(250))")
# mycursor.execute("CREATE TABLE User_Roster (userID bigint, playerID int)")
#mycursor.execute("CREATE TABLE Players (playerID int PRIMARY KEY AUTO_INCREMENT"
#                  ", position VARCHAR(250), name VARCHAR(250))")

# mycursor.execute("SHOW TABLES")
#
# for x in mycursor:
#     print(x)
#
#
# mycursor.execute("SELECT * FROM Users")
# for x in mycursor:
#     print(x)

