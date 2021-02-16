import mysql.connector as mysql
from config import PASSWORD

mydb = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = PASSWORD,
    database = "users"
)

mycursor = mydb.cursor()

# Tables Created
# mycursor.execute("CREATE TABLE Users (userID bigint PRIMARY KEY, team_name "
#                 "VARCHAR(250))")
# mycursor.execute("CREATE TABLE User_Roster (userID bigint, "
#                  "FOREIGN KEY(userID) REFERENCES Users(userID), "
#                  "position VARCHAR(250), name VARCHAR(250), team VARCHAR(250))")

