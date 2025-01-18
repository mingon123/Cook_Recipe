import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
    database="recipes",
    auth_plugin='mysql_native_password'
)
cursor = db.cursor()

# SQL = 'DROP TABLE replies'
#
# cursor.execute(SQL)

SQL = '''
CREATE TABLE IF NOT EXISTS replies (
    replyNo INT AUTO_INCREMENT PRIMARY KEY,
    author VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    targetArticle INT NOT NULL,
    FOREIGN KEY (targetArticle) REFERENCES recipes_data1(번호)
)
'''

cursor.execute(SQL)

cursor.close()
db.close()
