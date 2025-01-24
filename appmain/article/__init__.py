import mysql.connector
from flask import Flask

# MySQL 연결 설정
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
    database="recipes",
    auth_plugin='mysql_native_password'
)
cursor = db.cursor()

# articles 테이블 생성 쿼리
create_table_query = """
CREATE TABLE IF NOT EXISTS recipes_data1 (
    번호 INT AUTO_INCREMENT PRIMARY KEY,
    메뉴명 VARCHAR(255),
    재료 TEXT,
    조리방법 VARCHAR(50),
    요리종류 VARCHAR(50),
    열량 INT,
    탄수화물 INT,
    단백질 INT,
    지방 INT,
    나트륨 INT,
    완성이미지 TEXT,
    저감조리법_TIP TEXT,
    조리순서1 TEXT,
    이미지1 TEXT,    
    조리순서2 TEXT,
    이미지2 TEXT, 
    조리순서3 TEXT,
    이미지3 TEXT, 
    조리순서4 TEXT,
    이미지4 TEXT, 
    조리순서5 TEXT,
    이미지5 TEXT, 
    조리순서6 TEXT,
    이미지6 TEXT
);
"""

cursor.execute(create_table_query)

cursor.close()
db.close()
