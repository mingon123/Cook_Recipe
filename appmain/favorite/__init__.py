import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
    database="recipes",
    auth_plugin='mysql_native_password'
)
cursor = db.cursor()

SQL_user_favorites = '''
CREATE TABLE IF NOT EXISTS user_favorites (
    user_id INT NOT NULL,
    article_no INT NOT NULL,
    added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, article_no),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (article_no) REFERENCES recipes_data1(번호)
);
'''

cursor.execute(SQL_user_favorites)
db.commit()

cursor.close()
db.close()