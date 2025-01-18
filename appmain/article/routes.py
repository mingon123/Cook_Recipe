import os
from flask import Blueprint, send_from_directory, make_response, jsonify, request, session, redirect, url_for, \
    current_app as app, render_template
import mysql.connector
from appmain import app
from appmain.utils import verifyJWT, getJWTContent
from datetime import datetime

article = Blueprint('article', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0000",
        database="recipes",
        auth_plugin='mysql_native_password'
    )


@article.route('/api/article/recent', methods=['GET'])
def getRecentArticles():
    conn = get_db_connection()
    cursor = conn.cursor()

    SQL = 'SELECT 번호, 메뉴명, 재료, 조리방법, 요리종류, 열량, 탄수화물, 단백질, 지방, 나트륨 \
           FROM recipes_data1 ORDER BY 번호 DESC LIMIT 6'

    cursor.execute(SQL)

    result = cursor.fetchall()

    cursor.close()

    recentArticleDics = [{"articleNo": article[0], "recipeName": article[1], "ingredients": article[2],
                          "cookingMethod": article[3], "cuisineType": article[4], "calories": article[5],
                          "carbohydrates": article[6], "protein": article[7], "fat": article[8], "sodium": article[9]}
                         for article in result]

    return make_response(jsonify({"success": True, "articles": recentArticleDics}), 200)

@article.route('/display_article/<int:articleNo>', methods=['GET'])
def displayArticlePage(articleNo):
    # user_id = request.args.get("user_id")
    user_id = session.get("user_id")
    print("User ID:", user_id)
    if user_id:
        try:
            save_user_visit(str(user_id), articleNo)
            return render_template('display_article.html', user_id=user_id)
        except Exception as e:
            print(f"Error saving user visit: {e}")

    return send_from_directory(app.root_path, 'templates/display_article.html')

def save_user_visit(user_id, articleNo):
    conn = get_db_connection()
    cursor = conn.cursor()

    visit_date = datetime.now()

    SQL = 'INSERT INTO user_visits (user_id, articleNo, visit_date) VALUES (%s, %s, %s)'
    cursor.execute(SQL, (user_id, articleNo, visit_date))
    conn.commit()

    cursor.close()
    conn.close()



# @app.route('/api/user/visit_recipe', methods=['POST'])
# def add_user_visit():
#     data = request.form
#     user_id = data.get("user_id")
#     articleNo = data.get("articleNo")
#
#     print("Received user_id:", user_id)
#     print("Received articleNo:", articleNo)
#
#     save_user_visit(user_id, articleNo)
#
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     # 이미 방문한 기록이 있는지 확인
#     SQL_check = 'SELECT COUNT(*) FROM user_visits WHERE user_id = %s AND articleNo = %s'
#     cursor.execute(SQL_check, (user_id, articleNo))
#     count = cursor.fetchone()[0]
#
#     if count == 0:
#         # 방문한 기록이 없으면 새로운 레코드 삽입
#         SQL_insert = 'INSERT INTO user_visits (user_id, articleNo) VALUES (%s, %s)'
#         cursor.execute(SQL_insert, (user_id, articleNo))
#         conn.commit()
#
#     cursor.close()
#     conn.close()
#
#     return jsonify({"success": True}), 200


def translateCategory(catId):
    cuisineType = '기타'

    if catId == 0:
        cuisineType = '국&찌개'
    elif catId == 1:
        cuisineType = '기타'
    elif catId == 2:
        cuisineType = '반찬'
    elif catId == 3:
        cuisineType = '밥'
    elif catId == 4:
        cuisineType = '일품'
    elif catId == 5:
        cuisineType = '후식'
    else:
        cuisineType = '기타'

    return cuisineType

@article.route('/api/article/display', methods=['GET', 'POST'])
def displayArticle():
    data = request.form
    articleNo = data.get("articleNo")

    conn = get_db_connection()
    cursor = conn.cursor()

    payload = {"success": False}

    SQL = '''SELECT 메뉴명, 재료, 조리방법, 요리종류, 열량, 탄수화물, 단백질, 지방, 나트륨, 완성이미지, 저감조리법_TIP, 
           조리순서1, 이미지1, 조리순서2, 이미지2, 조리순서3, 이미지3, 조리순서4, 이미지4, 조리순서5, 이미지5, 조리순서6, 이미지6 
           FROM recipes_data1 WHERE `번호`=%s'''
    cursor.execute(SQL, (articleNo,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        article = {
            "recipeName": result[0],
            "ingredients": result[1],
            "cookingMethod": result[2],
            "cuisineType": result[3],
            "calories": result[4],
            "carbohydrates": result[5],
            "protein": result[6],
            "fat": result[7],
            "sodium": result[8],
            "att_file_no_mk": result[9],
            "rcp_na_tip": result[10],
            "manual1": result[11],
            "manual_img1": result[12],
            "manual2": result[13],
            "manual_img2": result[14],
            "manual3": result[15],
            "manual_img3": result[16],
            "manual4": result[17],
            "manual_img4": result[18],
            "manual5": result[19],
            "manual_img5": result[20],
            "manual6": result[21],
            "manual_img6": result[22]
        }
        payload = {"success": True, "article": article}
    else:
        payload = {"success": False, "article": None}

    return make_response(jsonify(payload), 200)


@article.route('/api/article/search', methods=['POST'])
def searchArticles():
    data = request.form
    searchKeyword = data.get("searchKeyword")
    excludedIngredients = data.get("excludedIngredients")
    noDairy = data.get("noDairy")
    vegetarian = data.get("vegetarian")
    vegan = data.get("vegan")
    nut = data.get("nut")
    cuisineType = data.get("cuisineType")

    payload = {"success": False}


    authToken = request.headers.get("Authorization")
    if not authToken or not authToken.startswith('Bearer '):
        return jsonify({"message": "Authorization token is required"}), 401

    authToken = authToken[7:]
    if not verifyJWT(authToken):
        return jsonify({"message": "Invalid or expired token"}), 401

    user_info = getJWTContent(authToken)
    if not user_info:
        return jsonify({"message": "Unable to extract user information from token"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT height, weight, allergies, weight_loss, diabetes, high_bp, cholesterol FROM users WHERE user_id = %s",
        (user_info['user_id'],))
    user_health = cursor.fetchone()

    if cursor:
        SQL = 'SELECT 번호, 메뉴명, 재료, 조리방법, 요리종류, 열량, 탄수화물, 단백질, 지방, 나트륨 FROM recipes_data1 WHERE 1=1'


        condition_statements = []

        if cuisineType:
            condition_statements.append(f"요리종류 = '{cuisineType}'")

        if user_health:
            height, weight = user_health[0], user_health[1]

            if height is not None and weight is not None:
                bmi = (weight / ((height / 100) ** 2))

                if bmi < 18.5:
                    condition_statements.append('열량 > 500')
                elif bmi >= 25 and bmi <= 29.9:
                    condition_statements.append('열량 < 300')
                elif bmi >= 30:
                    condition_statements.append('열량 < 250')
            else:
                bmi = None
        else:
            bmi = None

        if user_health[3] == 1: #weight_loss
            order_clause = 'ORDER BY 열량 ASC'
        else:
            order_clause = 'ORDER BY 번호 DESC'

        if user_health[4] == 1:  # diabetes
            condition_statements.append('탄수화물 < 20')
        if user_health[5] == 1:  # high_bp
            condition_statements.append('나트륨 < 140')
        if user_health[6] == 1:  # cholesterol
            condition_statements.append('지방 < 20')

        if condition_statements:
            SQL += ' AND ' + ' AND '.join(condition_statements)


        if searchKeyword:
            search_conditions = []
            for keyword in searchKeyword.split(','):
                keyword = keyword.strip()
                if keyword:
                    search_conditions.append('재료 LIKE "%{}%"'.format(keyword))
            if search_conditions:
                SQL += ' AND (' + ' AND '.join(search_conditions) + ')'

        if excludedIngredients:
            excluded_list = excludedIngredients.split(',')
            for excluded in excluded_list:
                SQL += ' AND 재료 NOT LIKE "%{}%"'.format(excluded.strip())

        if noDairy == 'true':
            SQL += (' AND (재료 NOT LIKE "%우유%" AND 재료 NOT LIKE "%치즈%" AND 재료 NOT LIKE "%버터%" '
                    'AND 재료 NOT LIKE "%요거트%" AND 재료 NOT LIKE "%크림%" AND 재료 NOT LIKE "%젤라틴%")')

        if vegetarian == 'true':
            SQL += (' AND (재료 NOT LIKE "%고기%" AND 재료 NOT LIKE "%닭고기%" AND 재료 NOT LIKE "%돼지고기%" '
                    'AND 재료 NOT LIKE "%소고기%" AND 재료 NOT LIKE "%어류%" AND 재료 NOT LIKE "%새우%" AND 재료 NOT LIKE "%꽃게%" AND 재료 NOT LIKE "%게살%")')

        if vegan == 'true':
            SQL += (
                ' AND (재료 NOT LIKE "%고기%" AND 재료 NOT LIKE "%닭고기%" AND 재료 NOT LIKE "%돼지고기%" AND 재료 NOT LIKE "%소고기%" '
                'AND 재료 NOT LIKE "%어류%" AND 재료 NOT LIKE "%새우%" AND 재료 NOT LIKE "%꽃게%" AND 재료 NOT LIKE "%게살%" '
                'AND 재료 NOT LIKE "%우유%" AND 재료 NOT LIKE "%치즈%" AND 재료 NOT LIKE "%버터%" AND 재료 NOT LIKE "%요거트%" '
                'AND 재료 NOT LIKE "%크림%" AND 재료 NOT LIKE "%계란%" AND 재료 NOT LIKE "%꿀%" AND 재료 NOT LIKE "%젤라틴%")')

        if nut == 'true':
            SQL += (' AND (재료 NOT LIKE "%땅콩%" AND 재료 NOT LIKE "%호두%" AND 재료 NOT LIKE "%아몬드%" '
                    'AND 재료 NOT LIKE "%캐슈넛%" AND 재료 NOT LIKE "%피스타치오%" AND 재료 NOT LIKE "%브라질넛%" '
                    'AND 재료 NOT LIKE "%헤이즐넛%" AND 재료 NOT LIKE "%마카다미아%" AND 재료 NOT LIKE "%피칸%" '
                    'AND 재료 NOT LIKE "%잣%")')

        if user_health and user_health[2]: #allergies
            allergies = user_health[2].split(',')
            for allergy in allergies:
                SQL += f' AND 재료 NOT LIKE "%{allergy.strip()}%"'

        SQL += ' ' + order_clause
        # SQL += 'ORDER BY 번호 DESC'

        cursor.execute(SQL)
        result = cursor.fetchall()

        cursor.close()
        conn.close()

    searchResults = []

    if len(result) > 0:
        for article in result:
            searchResults.append({"articleNo": article[0], "recipeName": article[1], "ingredients": article[2], \
                                  "cookingMethod": article[3], "cuisineType": article[4], "calories": article[5], \
                                  "carbohydrates": article[6], "protein": article[7], "fat": article[8], "sodium": article[9]})

        payload = {"success": True, "articles": searchResults}

    return make_response(jsonify(payload), 200)

