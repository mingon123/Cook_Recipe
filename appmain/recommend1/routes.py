import os
from flask import Blueprint, send_from_directory, make_response, jsonify, request, session, current_app as app, render_template
import mysql.connector
from appmain import app
from appmain.recommend1 import manage_user_visits
from datetime import datetime

from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

recommend1 = Blueprint('recommend1', __name__)

current_dir = os.path.dirname(__file__)
model_relative_path = 'food2vec.model'
model_path = os.path.join(current_dir, model_relative_path)
food2vec_model = Word2Vec.load(model_path)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0000",
        database="recipes",
        auth_plugin='mysql_native_password'
    )


def tokenize_text(text):
    if not isinstance(text, str):
        return []
    return word_tokenize(text)


@recommend1.route('/recommend1')
def show_recommend():
    limit = 20
    topn = 5

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "로그인 되어 있지 않습니다"}), 404

    recommended_recipes = get_recommended_recipes_data(limit, topn, user_id)

    return render_template('recommend1.html', recommended_recipes=recommended_recipes)


@recommend1.route('/api/recommend1', methods=['GET'])
def get_recommended_recipes():
    limit = 20
    topn = 5

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "사용자 ID를 찾을 수 없습니다."}), 404

    recommended_recipes = get_recommended_recipes_data(limit, topn, user_id)

    if not recommended_recipes:
        return jsonify({"success": False, "message": "사용자가 최근에 조회한 레시피가 없습니다."}), 200

    return jsonify({"success": True, "recommended_recipes": recommended_recipes}), 200


# 방문레시피 기록 저장
def save_recently_visited_recipe(user_id, recipe_number):
    if 'recently_visited_recipes' not in session:
        session['recently_visited_recipes'] = []
    session['recently_visited_recipes'].append(recipe_number)
    if len(session['recently_visited_recipes']) > 10:
        del session['recently_visited_recipes'][0]


# 방문한 레시피 목록 가져오기
def get_recently_visited_recipes():
    return session.get('recently_visited_recipes', [])


# 추천 레시피 데이터 가져옴
def get_recommended_recipes_data(limit, topn, user_id):
    visited_recipe_numbers = get_visited_recipe_numbers(user_id, limit)
    recommended_recipes_data = []

    for recipe_number in visited_recipe_numbers:
        if recipe_number not in get_recently_visited_recipes():
            similar_recipes = find_similar_recipes(recipe_number, topn)

            for recipe in similar_recipes:
                is_duplicate = False
                for recommended_recipe in recommended_recipes_data:
                    if recommended_recipe['articleNo'] == recipe[0]:
                        is_duplicate = True
                        break

                if not is_duplicate:
                    article_details = get_article_details(recipe[0])
                    nutrition_info = get_nutrition_info(recipe[0])
                    recommended_recipes_data.append({
                        "articleNo": recipe[0],
                        "recipeName": article_details[0],
                        "ingredients": article_details[1],
                        "cookingMethod": nutrition_info[0],
                        "cuisineType": nutrition_info[1],
                        "calories": nutrition_info[2],
                        "carbohydrates": nutrition_info[3],
                        "protein": nutrition_info[4],
                        "fat": nutrition_info[5],
                        "sodium": nutrition_info[6],
                        "similarity": recipe[1]
                    })
    recommended_recipes_data = sorted(recommended_recipes_data, key=lambda x: x["similarity"], reverse=True)
    return recommended_recipes_data[:20]


# 유사한 레시피 찾기
def find_similar_recipes(articleNo, topn=5):
    target_details = get_article_details(articleNo)
    if not target_details:
        return []

    target_vector = compute_article_vector(target_details)
    if target_vector is None:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()

    SQL = 'SELECT 번호, 메뉴명, 재료 FROM recipes_data1 WHERE 번호 != %s'
    cursor.execute(SQL, (articleNo,))
    all_recipes = cursor.fetchall()

    cursor.close()
    conn.close()

    similarities = []
    for recipe in all_recipes:
        recipeNo = recipe[0]
        recipe_vector = compute_article_vector((recipe[1], recipe[2]))
        if recipe_vector is None:
            continue
        similarity = cosine_similarity(target_vector, recipe_vector)
        similarities.append((recipeNo, similarity.item()))

    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:topn]


# 주어진 레시피 임베딩 벡터 계산
def compute_article_vector(article_details):
    recipe_name = article_details[0]
    ingredients = article_details[1]

    recipe_tokens = tokenize_text(recipe_name + " " + ingredients)

    recipe_vectors = []
    for token in recipe_tokens:
        if token in food2vec_model.wv.key_to_index:
            recipe_vectors.append(food2vec_model.wv[token])

    if not recipe_vectors:
        return None

    recipe_vector_sum = np.mean(recipe_vectors, axis=0)
    return recipe_vector_sum.reshape(1, -1)


# 각 레시피 메뉴명, 재료를 가져옴
def get_article_details(articleNo):
    conn = get_db_connection()
    cursor = conn.cursor()

    SQL = 'SELECT 메뉴명, 재료, 완성이미지 FROM recipes_data1 WHERE 번호 = %s'
    cursor.execute(SQL, (articleNo,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result


# 각 레시피 영양 정보 가져옴
def get_nutrition_info(articleNo):
    conn = get_db_connection()
    cursor = conn.cursor()

    SQL = 'SELECT 조리방법, 요리종류, 열량, 탄수화물, 단백질, 지방, 나트륨 FROM recipes_data1 WHERE 번호 = %s'
    cursor.execute(SQL, (articleNo,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result


# 유사한 레시피 가져옴
@recommend1.route('/api/recommend/similar/<int:articleNo>', methods=['GET'])
def getSimilarRecipes(articleNo):
    similar_recipes = find_similar_recipes(articleNo)
    similar_recipes_info = [{"articleNo": recipe[0], "similarity": recipe[1]} for recipe in similar_recipes]

    return make_response(jsonify({"success": True, "similar_recipes": similar_recipes_info}), 200)


# 특정 사용자가 방문한 레시피 번호 목록을 가져옴
def get_visited_recipe_numbers(user_id, limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()

    SQL = 'SELECT articleNo FROM user_visits WHERE user_id = %s ORDER BY visit_date DESC LIMIT %s'
    cursor.execute(SQL, (user_id, limit))
    visited_recipe_numbers = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return visited_recipe_numbers


# 레시피 상세포인트 표시 엔드포인트
@recommend1.route('/display_article/<int:articleNo>', methods=['GET'])
def displayArticlePage(articleNo):
    user_id = session.get("user_id")
    # print("User ID:", user_id)
    if user_id:
        try:
            save_user_visit(str(user_id), articleNo)
            return render_template('display_article.html', user_id=user_id)
        except Exception as e:
            print(f"Error saving user visit: {e}")

    return send_from_directory(app.root_path, 'templates/display_article.html')


# 레시피 조회 기록 저장
def save_user_visit(user_id, articleNo):
    conn = get_db_connection()
    cursor = conn.cursor()

    visit_date = datetime.now()

    cursor.execute('SELECT * FROM user_visits WHERE user_id = %s AND articleNo = %s', (user_id, articleNo))
    existing_visit = cursor.fetchone()

    if existing_visit:
        SQL = 'UPDATE user_visits SET visit_date = %s WHERE user_id = %s AND articleNo = %s'
        cursor.execute(SQL, (visit_date, user_id, articleNo))
    else:
        SQL = 'INSERT INTO user_visits (user_id, articleNo, visit_date) VALUES (%s, %s, %s)'
        cursor.execute(SQL, (user_id, articleNo, visit_date))

    conn.commit()

    manage_user_visits()

    cursor.close()
    conn.close()

# 로그인 기록 가져옴(사이드바)
@recommend1.route('/api/article/recent_user_visits', methods=['GET'])
def getRecentUserVisits():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "User not logged in"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    SQL = '''
    SELECT rv.articleNo, rd.메뉴명, rd.완성이미지 
    FROM user_visits rv 
    JOIN recipes_data1 rd ON rv.articleNo = rd.번호 
    WHERE rv.user_id = %s 
    ORDER BY rv.visit_date DESC 
    LIMIT 5
    '''
    cursor.execute(SQL, (user_id,))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    recentArticleDics = [{"articleNo": article[0], "recipeName": article[1], "image": article[2]}
                         for article in result]

    return make_response(jsonify({"success": True, "articles": recentArticleDics}), 200)


# 로그아웃
@recommend1.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return make_response(jsonify({"success": True, "message": "Logged out successfully"}), 200)
