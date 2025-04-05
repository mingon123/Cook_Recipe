import os
from flask import Blueprint, jsonify, request, session, render_template
import mysql.connector
from datetime import datetime

favorite = Blueprint('favorite', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0000",
        database="recipes",
        auth_plugin='mysql_native_password'
    )

@favorite.route('/favorites')
def favorites_page():
    return render_template('favorites.html')

@favorite.route('/api/favorite', methods=['POST'])
def add_favorite():
    user_id = session.get("user_id")
    article_no = request.json.get('article_no')

    if not user_id:
        return jsonify({"success": False, "message": "로그인 후에 즐겨찾기 추가가 가능합니다."}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_favorites WHERE user_id = %s AND article_no = %s', (user_id, article_no))
    favorite = cursor.fetchone()

    if favorite:
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "즐겨찾기 상태를 확인했습니다."}), 200

    cursor.execute('INSERT INTO user_favorites (user_id, article_no) VALUES (%s, %s)', (user_id, article_no))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True, "message": "즐겨찾기 추가됨"}), 200

@favorite.route('/api/favorite/<int:article_no>', methods=['DELETE'])
def remove_favorite(article_no):
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"success": False, "message": "로그인 후에 즐겨찾기 추가가 가능합니다."}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_favorites WHERE user_id = %s AND article_no = %s', (user_id, article_no))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True, "message": "즐겨찾기 삭제됨"}), 200

@favorite.route('/api/favorite', methods=['GET'])
def get_favorites():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"success": False, "message": "로그인 후에 즐겨찾기 추가가 가능합니다."}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.번호, r.메뉴명, r.이미지6, r.이미지5, r.이미지4, r.이미지3, r.이미지2, r.이미지1, 1 AS isFavorite
        FROM user_favorites uf 
        JOIN recipes_data1 r ON uf.article_no = r.번호 
        WHERE uf.user_id = %s
        ORDER BY uf.added_date DESC
    ''', (user_id,))
    favorites = cursor.fetchall()
    cursor.close()
    conn.close()

    favorite_recipes = []
    for fav in favorites:
        image = fav[2] or fav[3] or fav[4] or fav[5] or fav[6] or fav[7]
        favorite_recipes.append({
            "articleNo": fav[0],
            "recipeName": fav[1],
            "image": image,
            "isFavorite": fav[8]
        })

    return jsonify({"success": True, "favorites": favorite_recipes}), 200

@favorite.route('/api/favorite/status/<int:article_no>', methods=['GET'])
def check_favorite_status(article_no):
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"success": False, "message": "로그인 후에 즐겨찾기 추가가 가능합니다."}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_favorites WHERE user_id = %s AND article_no = %s', (user_id, article_no))
    favorite = cursor.fetchone()
    cursor.close()
    conn.close()

    return jsonify({"success": True, "is_favorite": favorite is not None}), 200

@favorite.route('/api/favorite/<int:article_no>', methods=['POST', 'DELETE'])
def toggle_favorite(article_no):
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"success": False, "message": "로그인 후에 즐겨찾기 추가가 가능합니다."}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        cursor.execute('SELECT * FROM user_favorites WHERE user_id = %s AND article_no = %s', (user_id, article_no))
        favorite = cursor.fetchone()

        if favorite:
            cursor.close()
            conn.close()
            return jsonify({"success": True, "message": "즐겨찾기 상태를 확인했습니다."}), 200

        cursor.execute('INSERT INTO user_favorites (user_id, article_no) VALUES (%s, %s)', (user_id, article_no))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "즐겨찾기 추가됨"}), 200

    elif request.method == 'DELETE':
        cursor.execute('DELETE FROM user_favorites WHERE user_id = %s AND article_no = %s', (user_id, article_no))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "즐겨찾기 삭제됨"}), 200

