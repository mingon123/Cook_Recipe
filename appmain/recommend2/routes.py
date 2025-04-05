import os
from flask import Blueprint, send_from_directory, make_response, jsonify, session, current_app as app, render_template
import mysql.connector
from appmain import app
from appmain.recommend1 import manage_user_visits
from datetime import datetime

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import faiss
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

recommend2 = Blueprint('recommend2', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0000",
        database="recipes",
        auth_plugin='mysql_native_password'
    )

file_path = os.path.join(os.path.dirname(__file__), 'processed_recipes.csv')
df = pd.read_csv(file_path, sep='\t', encoding='cp949')

df = df[['recipeName', 'ingredients']]
df['ingredients'] = df['ingredients'].astype(str).fillna('')

train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

sbert_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 임베딩 생성 함수
def generate_embeddings(model, texts):
    return model.encode(texts)

# SBERT 임베딩 생성
sbert_train_embeddings = generate_embeddings(sbert_model, train_df['ingredients'].tolist())
sbert_test_embeddings = generate_embeddings(sbert_model, test_df['ingredients'].tolist())

# 임베딩을 DataFrame에 추가
train_df['embeddings'] = list(sbert_train_embeddings)
test_df['embeddings'] = list(sbert_test_embeddings)


# # Faiss 인덱스 생성 및 학습
# embedding_size = weighted_train_embeddings.shape[1]
# index = faiss.IndexFlatL2(embedding_size)
# index.add(np.vstack(train_df['embeddings'].values))
#
# # Faiss 유사도 계산 함수
# def get_recommendations_faiss(target_embedding, df, index, top_n=5):
#     target_embedding = np.expand_dims(target_embedding, axis=0)
#     distances, indices = index.search(target_embedding, top_n + 1)
#     recommended_indices = indices[0][1:]
#     similarities = 1 / (1 + distances[0][1:])
#     return df.iloc[recommended_indices], similarities




#패키지 쓰지 않고 코사인 유사도 + 유클리드 거리 계산
def cosine_similarity_manual(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)

def euclidean_distance_manual(vec1, vec2):
    return np.sqrt(np.sum((vec1 - vec2) ** 2))

def combined_similarity(vec1, vec2, alpha=0.5):
    cos_sim = cosine_similarity_manual(vec1, vec2)
    euc_dist = euclidean_distance_manual(vec1, vec2)
    euc_sim = 1 / (1 + euc_dist)
    combined_sim = alpha * cos_sim + (1 - alpha) * euc_sim
    return combined_sim

def get_recommendations_combined(target_embedding, embeddings, df, top_n=5, alpha=0.5):
    similarities = np.array([combined_similarity(target_embedding, embedding, alpha) for embedding in embeddings])
    top_indices = similarities.argsort()[-top_n:][::-1]
    return df.iloc[top_indices], similarities[top_indices]




# # 코사인 유사도
# def get_recommendations_cosine(target_embedding, train_embeddings, train_df, top_n=5):
#     similarities = cosine_similarity(target_embedding, train_embeddings)[0]
#     top_indices = similarities.argsort()[-top_n-1:-1][::-1]
#     return train_df.iloc[top_indices], similarities[top_indices]
#
# # 유클리드 거리
# def get_recommendations_euclidean(target_embedding, embeddings, df, top_n=5):
#     distances = euclidean_distances(target_embedding, embeddings)[0]
#     top_indices = distances.argsort()[:top_n]
#     return df.iloc[top_indices], distances[top_indices]




# 코사인유사도 + 유클리드 거리 계산
def hybrid_similarity(vec1, vec2, alpha=0.5):
    cos_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    euc_dist = np.linalg.norm(vec1 - vec2)
    return alpha * cos_sim + (1 - alpha) * (1 / (1 + euc_dist))

def get_recommendations_hybrid(target_embedding, df, embeddings, top_n=5):
    similarities = np.array([hybrid_similarity(target_embedding, emb) for emb in embeddings])
    top_indices = similarities.argsort()[-top_n:][::-1]
    return df.iloc[top_indices], similarities[top_indices]



#
# # 유사도 계산 및 평균 유사도 계산 함수
# def calculate_average_similarity(method, target_embedding, df, embeddings, index=None):
#     if method == 'faiss':
#         _, similarities = get_recommendations_faiss(target_embedding, df, index)
#     elif method == 'combined':
#         _, similarities = get_recommendations_combined(target_embedding, embeddings, df)
#     elif method == 'hybrid':
#         _, similarities = get_recommendations_hybrid(target_embedding, df, embeddings)
#     return np.mean(similarities)
#
# # 검증 셋과 테스트 셋의 각 레시피에 대해 평균 유사도 계산
# methods = ['faiss', 'combined', 'hybrid']
# average_similarities_val = {method: [] for method in methods}
# average_similarities_test = {method: [] for method in methods}
#
# # 검증 셋에 대한 평균 유사도 계산
# for i in range(len(train_df)):
#     target_embedding = train_df['embeddings'].iloc[i]
#     for method in methods:
#         avg_sim = calculate_average_similarity(method, target_embedding, train_df, np.vstack(train_df['embeddings'].values), index)
#         average_similarities_val[method].append(avg_sim)
#
# # 테스트 셋에 대한 평균 유사도 계산
# for i in range(len(test_df)):
#     target_embedding = test_df['embeddings'].iloc[i]
#     for method in methods:
#         avg_sim = calculate_average_similarity(method, target_embedding, train_df, np.vstack(train_df['embeddings'].values), index)
#         average_similarities_test[method].append(avg_sim)
#
# # # 각 방법의 전체 평균 유사도 출력
# # print("2검증 데이터에 대한 평균 유사도 평가:")
# # for method in methods:
# #     print(f"{method}의 평균 유사도:", np.mean(average_similarities_val[method]))
# #
# # print("2테스트 데이터에 대한 평균 유사도 평가:")
# # for method in methods:
# #     print(f"{method}의 평균 유사도:", np.mean(average_similarities_test[method]))
#
#







@recommend2.route('/recommend2')
def show_recommend():
    topn = 20
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "로그인 되어 있지 않습니다"}), 404

    recommended_recipes, error_message = get_recommended_recipes(topn, user_id)
    if error_message:
        return jsonify({"success": False, "message": error_message}), 404

    return render_template('recommend2.html', recommended_recipes=recommended_recipes)

@recommend2.route('/api/recommend2', methods=['GET'])
def api_get_recommended_recipes():
    topn = 20
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "사용자 ID를 찾을 수 없습니다."}), 404

    recommended_recipes, error_message = get_recommended_recipes(topn, user_id)
    if error_message:
        return jsonify({"success": False, "message": error_message}), 404

    return jsonify({"success": True, "recommended_recipes": recommended_recipes}), 200

def get_recommended_recipes(topn, user_id):
    recently_visited = get_recently_visited_recipes(user_id)
    if not recently_visited:
        return None, "최근에 조회한 레시피가 없습니다"

    recommendations = []
    seen_recipes = set(recently_visited)

    for articleNo in recently_visited:
        article_details = get_article_details(articleNo)
        if article_details and article_details['메뉴명'] in test_df['recipeName'].values:
            target_embedding = test_df.loc[test_df['recipeName'] == article_details['메뉴명'], 'embeddings'].values[0]
            # similar_recipes, similarities = get_recommendations_faiss(target_embedding, train_df, index, topn)
            # similar_recipes, similarities = get_recommendations_combined(target_embedding, np.vstack(train_df['embeddings'].values), train_df, topn)
            similar_recipes, similarities = get_recommendations_hybrid(target_embedding, train_df, np.vstack(train_df['embeddings'].values), topn)
            for idx, (_, recipe) in enumerate(similar_recipes.iterrows()):
                similar_article_details = get_article_details_by_name(recipe['recipeName'])
                if similar_article_details and similar_article_details['번호'] not in seen_recipes:
                    seen_recipes.add(similar_article_details['번호'])
                    recommendations.append({
                        "articleNo": similar_article_details['번호'],
                        "recipeName": recipe['recipeName'],
                        "ingredients": recipe['ingredients'],
                        "cookingMethod": similar_article_details['조리방법'],
                        "cuisineType": similar_article_details['요리종류'],
                        "calories": similar_article_details['열량'],
                        "carbohydrates": similar_article_details['탄수화물'],
                        "protein": similar_article_details['단백질'],
                        "fat": similar_article_details['지방'],
                        "sodium": similar_article_details['나트륨'],
                        "image": similar_article_details['이미지'],
                        "similarity": float(similarities[idx])
                    })
    recommendations.sort(key=lambda x: x["similarity"], reverse=True)
    return recommendations[:20], None


def get_recently_visited_recipes(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    SQL = 'SELECT articleNo FROM user_visits WHERE user_id = %s ORDER BY visit_date DESC LIMIT 10'
    cursor.execute(SQL, (user_id,))
    recently_visited = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return recently_visited

def get_article_details(articleNo):
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)

    SQL = 'SELECT 번호, 메뉴명, 재료, 조리방법, 요리종류, 열량, 탄수화물, 단백질, 지방, 나트륨, 이미지6, 이미지5, 이미지4, 이미지3, 이미지2, 이미지1 FROM recipes_data1 WHERE 번호 = %s'
    cursor.execute(SQL, (articleNo,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return {
            '번호': result[0],
            '메뉴명': result[1],
            '재료': result[2],
            '조리방법': result[3],
            '요리종류': result[4],
            '열량': result[5],
            '탄수화물': result[6],
            '단백질': result[7],
            '지방': result[8],
            '나트륨': result[9],
            '이미지': result[10] or result[11] or result[12] or result[13] or result[14] or result[15]
        }
    return None

def get_article_details_by_name(recipeName):
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)

    SQL = 'SELECT 번호, 메뉴명, 재료, 조리방법, 요리종류, 열량, 탄수화물, 단백질, 지방, 나트륨, 이미지6, 이미지5, 이미지4, 이미지3, 이미지2, 이미지1 FROM recipes_data1 WHERE 메뉴명 = %s'
    cursor.execute(SQL, (recipeName,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return {
            '번호': result[0],
            '메뉴명': result[1],
            '재료': result[2],
            '조리방법': result[3],
            '요리종류': result[4],
            '열량': result[5],
            '탄수화물': result[6],
            '단백질': result[7],
            '지방': result[8],
            '나트륨': result[9],
            '이미지': result[10] or result[11] or result[12] or result[13] or result[14] or result[15]
        }
    return None


# 레시피 상세포인트 표시 엔드포인트
@recommend2.route('/display_article/<int:articleNo>', methods=['GET'])
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

#로그인 기록 가져옴(사이드바)
@recommend2.route('/api/article/recent_user_visits', methods=['GET'])
def getRecentUserVisits():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "User not logged in"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    SQL = '''
    SELECT rv.articleNo, rd.메뉴명, rd.이미지6, rd.이미지5, rd.이미지4, rd.이미지3, rd.이미지2, rd.이미지1 
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

    recentArticleDics = []
    for article in result:
        image = article[2] or article[3] or article[4] or article[5] or article[6] or article[7]
        recentArticleDics.append({"articleNo": article[0], "recipeName": article[1], "image": image})

    return make_response(jsonify({"success": True, "articles": recentArticleDics}), 200)

#로그아웃
@recommend2.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return make_response(jsonify({"success": True, "message": "Logged out successfully"}), 200)


@recommend2.route('/api/recommend/similar/<int:articleNo>', methods=['GET'])
def getSimilarRecipes(articleNo):
    article_details = get_article_details(articleNo)
    if not article_details:
        return jsonify({"success": False, "message": "레시피를 찾을 수 없습니다."}), 404

    target_embedding = test_df.loc[test_df['recipeName'] == article_details['메뉴명'], 'embeddings'].values[0]
    similar_recipes, similarities = get_recommendations_hybrid(target_embedding, train_df, np.vstack(train_df['embeddings'].values), top_n=5)

    similar_recipes_info = []
    for idx, (_, recipe) in enumerate(similar_recipes.iterrows()):
        similar_article_details = get_article_details_by_name(recipe['recipeName'])
        if similar_article_details:
            similar_recipes_info.append({
                "articleNo": similar_article_details['번호'],
                "recipeName": recipe['recipeName'],
                "image": similar_article_details['이미지'],
                "similarity": float(similarities[idx])
            })

    return make_response(jsonify({"success": True, "similar_recipes": similar_recipes_info}), 200)