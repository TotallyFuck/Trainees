import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np

# Загрузка данных из XLSX
df = pd.read_excel("C:/Users/User/Documents/GitHub/Trainees/DataBase/BB.xlsx")  # Укажите путь к вашему файлу
questions = df['Вопросы'].tolist()
answers = df['Ответы'].tolist()

# Создание эмбеддингов
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
question_embeddings = model.encode(questions, convert_to_tensor=True)

# Сохранение эмбеддингов и ответов
np.save('question_embeddings.npy', question_embeddings)
df.to_csv('BB_data.csv', index=False)
