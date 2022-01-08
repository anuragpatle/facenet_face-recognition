from deepface import DeepFace

obj = DeepFace.analyze(img_path="./photos/1_1.jpg", actions=['age', 'gender', 'race', 'emotion'])

print("obj: ", obj)
