import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
    database="recipes",
    auth_plugin='mysql_native_password'
)
cursor = db.cursor()

SQL = '''
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    passwd VARCHAR(255) NOT NULL,
    authkey VARCHAR(255),
    height INT,
    weight INT,
    weight_loss TINYINT(1),
    diabetes TINYINT(1),
    high_bp TINYINT(1),
    cholesterol TINYINT(1),
    allergies TEXT
);
'''
cursor.execute(SQL)

db.commit()

cursor.close()
db.close()