import pandas as pd
import numpy as np
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
import torch
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

# 레시피 데이터 불러오기
df = pd.read_csv('processed_recipes.csv', sep='\t', encoding='cp949')

# NLTK 토크나이저를 사용하여 토큰화 진행
def tokenize_text(text):
    if not isinstance(text, str):
        return []
    return word_tokenize(text)

# 모든 레시피 데이터를 토큰화
df['processed_recipeName'] = df['recipeName'].apply(tokenize_text)
df['processed_ingredients'] = df['ingredients'].apply(tokenize_text)

# TF-IDF 벡터화 진행
vectorizer = TfidfVectorizer(tokenizer=tokenize_text, lowercase=False)
tfidf_matrix = vectorizer.fit_transform(df['recipeName'].astype(str) + ' ' + df['ingredients'].astype(str))

# 단어와 TF-IDF 점수 매핑
feature_names = vectorizer.get_feature_names_out()
tfidf_scores = dict(zip(feature_names, tfidf_matrix.toarray().sum(axis=0)))

# 가중치를 적용한 데이터 준비
weighted_sentences = []
recipe_name_weight = 1
ingredient_weight = 2

for name, ingredients in zip(df['processed_recipeName'], df['processed_ingredients']):
    weighted_name = [(word, tfidf_scores.get(word, 0) * recipe_name_weight) for word in name]
    weighted_ingredients = [(word, tfidf_scores.get(word, 0) * ingredient_weight) for word in ingredients]
    weighted_sentences.append(weighted_name + weighted_ingredients)

def create_weighted_sentence(sentence_with_weights):
    weighted_sentence = []
    for word, weight in sentence_with_weights:
        weight = max(weight, 0.1)
        weighted_sentence.extend([word] * int(round(weight)))
    return weighted_sentence

# 가중치를 반영한 문장 데이터 생성
weighted_train_data = [create_weighted_sentence(sentence) for sentence in weighted_sentences]

# 데이터를 학습 세트, 검증 세트, 테스트 세트로 나누기
train_data, temp_data = train_test_split(weighted_train_data, test_size=0.4, random_state=42)
val_data, test_data = train_test_split(temp_data, test_size=0.5, random_state=42)

# Word2Vec 모델 학습
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = Word2Vec(sentences=train_data, vector_size=100, window=5, min_count=1, workers=8, sg=1, batch_words=1000)
print("Word2Vec 모델 학습 완료!")


# 모델 저장
model.save('food2vec.model')
print("모델 저장 완료!")

# 테스트 데이터로 모델 평가 함수
def evaluate_model(model, test_data):
    similarities = []
    for sentence in test_data:
        if len(sentence) < 2:
            continue
        vectors = [model.wv[word] for word in sentence if word in model.wv.key_to_index]
        if len(vectors) < 2:
            continue
        similarity_matrix = cosine_similarity(vectors)
        upper_triangle_indices = np.triu_indices_from(similarity_matrix, k=1)
        average_similarity = similarity_matrix[upper_triangle_indices].mean()
        similarities.append(average_similarity)
    return np.mean(similarities) if similarities else 0


# 검증 및 테스트 데이터 평가
val_accuracy = evaluate_model(model, val_data)
test_accuracy = evaluate_model(model, test_data)


print("모든 컬럼을 사용한 Food2Vec 모델 학습 및 저장 완료!")
print("검증 데이터에 대한 유사도 평가:", val_accuracy)
print("테스트 데이터에 대한 유사도 평가:", test_accuracy)

# for recipe in test_data:
#     print(recipe)

# vectors = model.wv.vectors
# tsne = TSNE(n_components=2, random_state=42)
# vectors_2d = tsne.fit_transform(vectors)
# df_2d = pd.DataFrame(vectors_2d, columns=['x', 'y'])
# plt.figure(figsize=(10, 8))
# sns.scatterplot(data=df_2d, x='x', y='y')
# plt.title('Word2Vec Embeddings')
# plt.xlabel('Dimension 1')
# plt.ylabel('Dimension 2')
# plt.show()

# print(df.sample(5))
# print(df.isnull().sum())
# print(df['ingredients'].head())
# df['ingredients_str'] = df['ingredients'].apply(lambda x: ','.join(x) if isinstance(x, list) else x)
# print(df.duplicated(subset=['recipeName', 'ingredients_str']).sum())



