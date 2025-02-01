import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re
import mysql.connector
import pandas as pd

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# 데이터베이스 연결 설정
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
    database="recipes",
    auth_plugin='mysql_native_password'
)

# 커서 생성
cursor = db.cursor()

# SQL 쿼리 실행
cursor.execute("SELECT 메뉴명, 재료, 조리방법, 요리종류 FROM recipes_data1")

# 데이터 모두 가져오기
rows = cursor.fetchall()

# 연결 종료
cursor.close()
db.close()

# 텍스트 전처리 함수
def preprocess_text(text):
    # HTML 태그 및 특수 문자 제거
    text = re.sub(r'<br\s*/?>', ' ', text)  # br 태그를 공백으로 치환
    text = re.sub(r'<[^>]+>', '', text)  # 기타 HTML 태그 제거
    text = re.sub(r'[\[\]●·]', '', text)  # 괄호 및 특수 기호 제거

    # 숫자와 'g', 'kg', 'Ts', 't', '컵', '개', '장', '쪽', '마리', '봉지' 단위 제거
    text = re.sub(r'\b\d+g\b', '', text)
    text = re.sub(r'\b\d+mg\b', '', text)
    text = re.sub(r'\b\d+kg\b', '', text)
    text = re.sub(r'\b\d+Ts\b', '', text)
    text = re.sub(r'\b\d+ts\b', '', text)
    text = re.sub(r'\b\d+t\b', '', text)
    text = re.sub(r'\b\d+ml\b', '', text)
    text = re.sub(r'\b\d+cm\b', '', text)
    text = re.sub(r'\b\d+g\b', '', text)
    text = re.sub(r'\b\d+컵\b', '', text)
    text = re.sub(r'\b\d+개\b', '', text)
    text = re.sub(r'\b\d+장\b', '', text)
    text = re.sub(r'\b\d+쪽\b', '', text)
    text = re.sub(r'\b\d+마리\b', '', text)
    text = re.sub(r'\b\d+봉지\b', '', text)
    text = re.sub(r'\d+', '', text)  # 모든 숫자 제거
    # 숫자와 단위 제거
    text = re.sub(r'\d+/?\d*\.?\s?\s*([a-zA-Z가-힣]*g|kg|ml|l|cm|mm|tsp|tbsp|T|cup|컵|개|큰술|작은술|줄기|봉|봉지|알|봉|팩|줌|대|쪽|약간|ts|Ts|t|각)?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(약간|적당량|소금|후춧가루|T|반|컵)\b', '', text)

    # 분수 표현 제거 (½, ¼, ⅓, ⅔ 등)
    text = re.sub(r'[½|⅓|¼|⅔|⅛|⅜|⅝|⅞|½|¼|⅓|⅔|⅛|]', '', text)
    text = re.sub(r'적당량|다진\w*|소개|필수재료|주재료|기준|간편식|재료|가정|필수|g', '', text)
    text = re.sub(r'\b(Ts|g)\b', '', text, flags=re.IGNORECASE)

    # 불필요한 텍스트 제거
    text = re.sub(r'인분|인분 기준|추가', '', text)
    text = re.sub(r'\[.*?\]', '', text)  # 대괄호 안의 텍스트 제거
    text = re.sub(r'[^\w\s]', '', text) # 특수 문자 제거
    text = re.sub(r'\s+', ' ', text).strip() # 공백 정리
    text = re.sub(r'적당량|다진\w*|큰술|작은술|알|컵|모|장식|약간|ⅹcm|m|xcm|ml|l', '', text)

    # 색상 및 불필요한 단위 제거
    text = re.sub(r'\s*\b(노랑|빨강|파랑|초록|주황|검정|흰|각|개|줌|봉|팩|대|개|묶음)\b', '', text)

    return text


# 전처리 적용
processed_data = []
for recipeName, ingredients, cookingMethod, cuisineType in rows:
    processed_recipeName = preprocess_text(recipeName)
    processed_ingredients = preprocess_text(ingredients)
    # processed_cookingMethod = preprocess_text(cookingMethod)
    # processed_cuisineType = preprocess_text(cuisineType)
    processed_data.append((processed_recipeName, processed_ingredients))

# 전처리된 데이터 출력
for data in processed_data:
    print(data)

# 전처리된 데이터를 데이터프레임으로 변환
df = pd.DataFrame(processed_data, columns=['recipeName', 'ingredients'])

# CSV 파일로 저장
df.to_csv('processed_recipes.csv', sep='\t', encoding='cp949', index=False)


