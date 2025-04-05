import os
from flask import Blueprint, send_from_directory, make_response, jsonify, session, current_app as app, render_template
import mysql.connector
from appmain import app
from appmain.recommend1 import manage_user_visits
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import torch
from torch import nn
from transformers import BertTokenizer, BertModel
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

recommend3 = Blueprint('recommend3', __name__)

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
tokenizer = BertTokenizer.from_pretrained('huawei-noah/TinyBERT_General_4L_312D')

# 임베딩 생성 함수
def generate_embeddings(model, texts):
    return model.encode(texts)

# SBERT 임베딩 생성
sbert_train_embeddings = generate_embeddings(sbert_model, train_df['ingredients'].tolist())
sbert_test_embeddings = generate_embeddings(sbert_model, test_df['ingredients'].tolist())


# 임베딩을 DataFrame에 추가
train_df['embeddings'] = list(sbert_train_embeddings)
test_df['embeddings'] = list(sbert_test_embeddings)





# Poly-Encoder 클래스 정의
class PolyEncoder(nn.Module):
    def __init__(self, bert_model_name='huawei-noah/TinyBERT_General_4L_312D', poly_m=16):
        super(PolyEncoder, self).__init__()
        self.poly_m = poly_m
        self.bert = BertModel.from_pretrained(bert_model_name).to('cuda')
        self.poly_code_embeddings = nn.Parameter(torch.randn(poly_m, self.bert.config.hidden_size).to('cuda'))

    def forward(self, context_input_ids, context_attention_mask, candidate_input_ids, candidate_attention_mask):
        context_outputs = self.bert(input_ids=context_input_ids, attention_mask=context_attention_mask)
        candidate_outputs = self.bert(input_ids=candidate_input_ids, attention_mask=candidate_attention_mask)
        context_embeddings = context_outputs.last_hidden_state[:, 0, :]
        candidate_embeddings = candidate_outputs.last_hidden_state[:, 0, :]
        poly_code_embeddings_expanded = self.poly_code_embeddings.unsqueeze(0).expand(context_embeddings.size(0), -1, -1)
        context_poly_similarity = torch.bmm(poly_code_embeddings_expanded, context_embeddings.unsqueeze(-1)).squeeze(-1)
        context_poly_similarity = torch.nn.functional.softmax(context_poly_similarity, dim=1)
        context_poly_embeddings = torch.bmm(context_poly_similarity.unsqueeze(1), poly_code_embeddings_expanded).squeeze(1)
        similarities = torch.nn.functional.cosine_similarity(context_poly_embeddings, candidate_embeddings)
        return similarities

poly_encoder_model = PolyEncoder(bert_model_name='huawei-noah/TinyBERT_General_4L_312D', poly_m=16).to('cuda')
tokenizer = BertTokenizer.from_pretrained('huawei-noah/TinyBERT_General_4L_312D')

def calculate_similarity_poly_encoder(model, tokenizer, context, candidates):
    context_inputs = tokenizer([context], return_tensors='pt', padding=True, truncation=True, max_length=128).to('cuda')
    candidate_inputs = tokenizer(candidates, return_tensors='pt', padding=True, truncation=True, max_length=128).to('cuda')
    with torch.no_grad():
        similarities = model(
            context_input_ids=context_inputs['input_ids'],
            context_attention_mask=context_inputs['attention_mask'],
            candidate_input_ids=candidate_inputs['input_ids'],
            candidate_attention_mask=candidate_inputs['attention_mask']
        )
    normalized_similarities = (similarities + 1) / 2
    return normalized_similarities.cpu().numpy().flatten()




# 평균 유사도 계산 및 출력
context = "example context ingredient"
candidates = ["candidate ingredient 1", "candidate ingredient 2", "candidate ingredient 3"]

similarities = calculate_similarity_poly_encoder(poly_encoder_model, tokenizer, context, candidates)
average_similarity = np.mean(similarities)

print(f"레시피 3 평균 유사도: {average_similarity:.4f}")








@recommend3.route('/recommend3')
def show_recommend():
    topn = 20
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "로그인 되어 있지 않습니다"}), 404

    recommended_recipes, error_message = get_recommended_recipes(topn, user_id)
    if error_message:
        return jsonify({"success": False, "message": error_message}), 404

    return render_template('recommend3.html', recommended_recipes=recommended_recipes)

@recommend3.route('/api/recommend3', methods=['GET'])
def api_get_recommended_recipes():
    topn = 20
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "사용자 ID를 찾을 수 없습니다."}), 404

    recommended_recipes, error_message = get_recommended_recipes(topn, user_id)
    if error_message:
        return jsonify({"success": False, "message": error_message}), 404

    return jsonify({"success": True, "recommended_recipes": recommended_recipes}), 200

def get_recommended_recipes(topn, user_id, similarity_threshold=0.1):
    recently_visited = get_recently_visited_recipes(user_id)
    if not recently_visited:
        return None, "최근에 조회한 레시피가 없습니다"

    recommendations = []
    seen_recipes = set(recently_visited)

    for articleNo in recently_visited:
        article_details = get_article_details(articleNo)
        if article_details and article_details['메뉴명'] in test_df['recipeName'].values:
            context = article_details['메뉴명']
            candidates = test_df['recipeName'].tolist()
            similarities = calculate_similarity_poly_encoder(poly_encoder_model, tokenizer, context, candidates)

            similar_recipes = test_df.iloc[np.argsort(similarities)[-topn:]]

            for idx, recipe in enumerate(similar_recipes.itertuples()):
                similar_article_details = get_article_details_by_name(recipe.recipeName)
                if similar_article_details and similar_article_details['번호'] not in seen_recipes:
                    seen_recipes.add(similar_article_details['번호'])
                    recommendations.append({
                        "articleNo": similar_article_details['번호'],
                        "recipeName": recipe.recipeName,
                        "ingredients": recipe.ingredients,
                        "cookingMethod": similar_article_details['조리방법'],
                        "cuisineType": similar_article_details['요리종류'],
                        "calories": similar_article_details['열량'],
                        "carbohydrates": similar_article_details['탄수화물'],
                        "protein": similar_article_details['단백질'],
                        "fat": similar_article_details['지방'],
                        "sodium": similar_article_details['나트륨'],
                        "image": similar_article_details['이미지'],
                        "similarity": float(similarities[np.argsort(similarities)[-topn:][idx]])
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
        image = next((img for img in result[10:] if img), None)
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
            '이미지': image
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
        image = next((img for img in result[10:] if img), None)
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
            '이미지': image
        }
    return None


# 레시피 상세포인트 표시 엔드포인트
@recommend3.route('/display_article/<int:articleNo>', methods=['GET'])
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
@recommend3.route('/api/article/recent_user_visits', methods=['GET'])
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
@recommend3.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return make_response(jsonify({"success": True, "message": "Logged out successfully"}), 200)

