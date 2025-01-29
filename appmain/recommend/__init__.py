import mysql.connector

def manage_user_visits():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="0000",
        database="recipes",
        auth_plugin='mysql_native_password'
    )
    cursor = db.cursor()

    SQL_user_visits = '''
    CREATE TABLE IF NOT EXISTS user_visits (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NULL,
        articleNo INT NOT NULL,
        visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id),
        FOREIGN KEY (articleNo) REFERENCES recipes_data1 (번호)
    );
    '''
    cursor.execute(SQL_user_visits)
    db.commit()

    SQL_delete_old_visits = '''
    DELETE FROM user_visits
    WHERE id NOT IN (
        SELECT id
        FROM (
            SELECT id
            FROM user_visits AS uv
            WHERE uv.user_id = user_visits.user_id
            ORDER BY visit_date DESC
            LIMIT 10
        ) AS recent_visits
    );
    '''
    cursor.execute(SQL_delete_old_visits)
    db.commit()

    cursor.close()
    db.close()