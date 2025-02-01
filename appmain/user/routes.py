from flask import Blueprint, send_from_directory, make_response, jsonify, request, session, Flask
import mysql.connector
import bcrypt
import secrets
import jwt
from datetime import datetime

from appmain import app
from appmain.utils import verifyJWT, getJWTContent

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0000",
        database="recipes",
        auth_plugin='mysql_native_password'
    )

user = Blueprint('user', __name__)

@user.route('/signup')
def signUp():
    return send_from_directory(app.root_path, 'templates/signup.html')

@user.route('/api/user/signup', methods=['POST'])
def register():
    data = request.form
    username = data.get("username")
    email = data.get("email")
    passwd = data.get("passwd")

    hashedPW = bcrypt.hashpw(passwd.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return make_response(jsonify({"success": False, "message": "이미 사용중인 아이디입니다."}), 409)

    SQL = 'INSERT INTO users (username, email, passwd) VALUES (%s, %s, %s)'
    cursor.execute(SQL, (username, email, hashedPW))
    conn.commit()

    cursor.close()
    conn.close()

    payload = {"success": True}
    return make_response(jsonify(payload), 200)


@user.route('/signin')
def signIn():
    return send_from_directory(app.root_path, 'templates/signin.html')

@user.route('/api/user/signin', methods=['POST'])
def getAuth():
    data = request.form
    email = data.get("email")
    passwd = data.get("passwd")

    conn = get_db_connection()
    cursor = conn.cursor()

    payload = {"authenticated": False, "email": '', "username": '', "authtoken": ''}

    if cursor:
        SQL = 'SELECT user_id, username, passwd FROM users WHERE email=%s'
        cursor.execute(SQL, (email,))
        result = cursor.fetchone()

        if result:
            hashed_password = result[2].encode('utf-8') if isinstance(result[2], str) else result[2]
            pwMatch = bcrypt.checkpw(passwd.encode('utf-8'), hashed_password)
            user_id = result[0]
            username = result[1]
        else:
            pwMatch = None

        if pwMatch:
            authkey = secrets.token_hex(16)

            SQL = 'UPDATE users SET authkey=%s WHERE user_id=%s'
            cursor.execute(SQL, (authkey, user_id))
            conn.commit()

            token = jwt.encode({"user_id": user_id, "email": email, "username": username, "authkey": authkey},
                               app.config["SECRET_KEY"], algorithm='HS256')

            session['user_id'] = user_id

            payload = {"authenticated": True, "email": email, "username": username, "authtoken": token}

        else:
            payload["message"] = "로그인에 실패하였습니다. 아이디나 비밀번호를 확인하세요."


        cursor.close()
    conn.close()

    return make_response(jsonify(payload), 200)


@user.route('/myinfo')
def myInfo():
    return send_from_directory(app.root_path, 'templates/mypage.html')

@user.route('/api/user/myinfo', methods=['POST'])
def getMyInfo():
    headerData = request.headers

    authToken = headerData.get("authtoken")

    payload = {"success": False}

    if authToken:
        isValid = verifyJWT(authToken)

        if isValid:
            token = getJWTContent(authToken)
            email = token["email"]

            conn = get_db_connection()
            cursor = conn.cursor()

            if cursor:
                SQL = 'SELECT username FROM users WHERE email=%s'
                cursor.execute(SQL, (email,))
                username = cursor.fetchone()[0]
                cursor.close()
            conn.close()

            payload = {"success": True, "username": username}

    return make_response(jsonify(payload), 200)

@user.route('/api/user/update', methods=['POST'])
def updateMyInfo():

    headerData = request.headers
    data = request.form

    authToken = headerData.get("authtoken")
    username = data.get("username")
    passwd = data.get("passwd")

    payload = {"success": False}

    if authToken:
        isValid = verifyJWT(authToken)

        if isValid:
            token = getJWTContent(authToken)
            email = token["email"]

            hashedPW = bcrypt.hashpw(passwd.encode('utf-8'), bcrypt.gensalt())

            conn = get_db_connection()
            cursor = conn.cursor()

            if cursor:
                if passwd:
                    SQL = 'UPDATE users SET username=%s, passwd=%s WHERE email=%s'
                    cursor.execute(SQL, (username, hashedPW, email))
                else:
                    SQL = 'UPDATE users SET username=%s WHERE email=%s'
                    cursor.execute(SQL, (username, email))
                conn.commit()

                payload["success"] = True
                payload["message"] = "비밀번호가 성공적으로 변경되었습니다."

                cursor.close()
            conn.close()

    return make_response(jsonify(payload), 200)




@app.route('/health')
def health():
    return send_from_directory(app.root_path, 'templates/health.html')

@app.route('/diabetes_check')
def diabetes_check():
    return send_from_directory(app.root_path, 'templates/diabetes_check.html')

@app.route('/high_bp_check')
def high_bp_check():
    return send_from_directory(app.root_path, 'templates/high_bp_check.html')

@app.route('/cholesterol_check')
def cholesterol_check():
    return send_from_directory(app.root_path, 'templates/cholesterol_check.html')

@user.route('/api/user/health', methods=['POST'])
def updateHealthInfo():
    authToken = request.headers.get('Authorization')
    if not authToken or not authToken.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401

    token = authToken.split('Bearer ')[1].strip()
    if not verifyJWT(token):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        email = getJWTContent(token).get('email')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users 
            SET height = %s, weight = %s, allergies = %s, weight_loss = %s, 
                diabetes = %s, high_bp = %s, cholesterol = %s 
            WHERE email = %s
            """,
            (data.get("height"), data.get("weight"), data.get("allergies"),
             int(data.get("weight_loss")), int(data.get("diabetes")),
             int(data.get("high_bp")), int(data.get("cholesterol")), email)
        )
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "건강 정보가 성공적으로 저장되었습니다."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



@user.route('/api/user/health', methods=['GET'])
def getHealthInfo():
    authToken = request.headers.get('Authorization')
    if not authToken or not authToken.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401

    token = authToken.split('Bearer ')[1].strip()
    if not verifyJWT(token):
        return jsonify({"error": "Unauthorized"}), 401

    email = getJWTContent(token).get('email')
    if not email:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT height, weight, allergies, weight_loss, diabetes, high_bp, cholesterol FROM users WHERE email=%s', (email,))
    user_health = cursor.fetchone()
    conn.close()

    if user_health:
        height, weight, allergies, weight_loss, diabetes, high_bp, cholesterol = user_health
        health_info = {
            "height": height,
            "weight": weight,
            "allergies": allergies,
            "weight_loss": bool(weight_loss),
            "diabetes": bool(diabetes),
            "high_bp": bool(high_bp),
            "cholesterol": bool(cholesterol)
        }
        return jsonify({"success": True, "healthInfo": health_info})
    else:
        return jsonify({"success": False, "message": "건강 정보를 찾을 수 없습니다."}), 404


