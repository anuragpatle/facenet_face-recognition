from deepface import DeepFace
import pandas as pd

df = DeepFace.find(img_path = "./static/uploaded_files/akshay.jpg", db_path = "./dataset1", enforce_detection=False)

# print(df.iloc[0].identity)
# print(df.iloc[0])
print(df.head())
