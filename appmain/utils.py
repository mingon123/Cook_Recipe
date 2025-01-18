import jwt
import mysql.connector
import secrets
from PIL import Image
import os

from appmain import app

def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0000",
        database="recipes",
        auth_plugin='mysql_native_password'
    )

def get_user_id_from_email(email):
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()

        if cursor:
            cursor.execute('SELECT user_id FROM users WHERE email=%s', (email,))
            user_id = cursor.fetchone()
            cursor.close()
        conn.close()

        return user_id[0] if user_id else None
    except Exception as e:
        print(f"Error getting user ID: {e}")
        return None

def verifyJWT(token):
    global authkey
    if token is None:
        return None
    else:
        try:
            decodedToken = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")
            if decodedToken:
                conn = get_mysql_connection()
                cursor = conn.cursor()

                if cursor:
                    cursor.execute('SELECT authkey FROM users WHERE email=%s', (decodedToken["email"],))
                    authkey = cursor.fetchone()

                    user_id = get_user_id_from_email(decodedToken["email"])

                    cursor.close()
                conn.close()

                if authkey and authkey[0] == decodedToken.get("authkey"):
                    return user_id
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f"Error decoding JWT: {e}")
            return None

def getJWTContent(token):
    try:
        decoded = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")
        if verifyJWT(token):
            return decoded
        return None
    except Exception as e:
        print(f"Error decoding JWT: {e}")
        return None


def savePic(pic, username):
    randHex = secrets.token_hex(8)
    _, fExt = os.path.splitext(pic.filename)
    picFileName = randHex + fExt
    picDir = os.path.join(app.static_folder, 'pics', username)
    picPath = os.path.join(picDir, picFileName)
    os.makedirs(picDir, exist_ok=True)

    with Image.open(pic) as image:
        image.save(picPath)

    return picFileName