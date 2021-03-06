import os
from flask import Flask, flash, request, redirect, url_for, session, render_template
from werkzeug.utils import secure_filename
from flask_session import Session
from deepface import DeepFace
from pathlib import Path
from deepface.basemodels import VGGFace
from pathlib import Path
import json
import requests


UPLOAD_FOLDER_FOR_RECOG = 'static/uploaded_files_for_recog'
DATASET_FOLDER = 'dataset'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
model = VGGFace.loadModel()

# Rest api end points
ROOT_SENTI_API_URI = "http://localhost:5000/facial-senti-api"
RAW_SENTI_API_URI = ROOT_SENTI_API_URI + "/raw_sentiments"
headers_ = {'Content-Type': 'application/json'}

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER_FOR_RECOG'] = UPLOAD_FOLDER_FOR_RECOG
app.config['DATASET_FOLDER'] = DATASET_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/face_app/hello', methods=['GET', 'POST'])
def welcome():
    return "Hello World!"


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/face_app/upload_for_recog', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    img_capture_time = request.form.get('current_time')
    img_capture_date = request.form.get('current_date')
    img_capture_datetime = request.form.get('current_datetime')
    
    img_capturing_device = request.form.get('device_id')
    print("img_capturing_device", img_capturing_device)
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER_FOR_RECOG'], filename))
        #print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')
        img_path = UPLOAD_FOLDER_FOR_RECOG  + '/' + filename
        # print('upload_image filename: ' + filename)
        
        df = DeepFace.find(img_path = img_path, db_path = "./dataset", model_name = 'VGG-Face', model = model, distance_metric = 'cosine', enforce_detection=False)
        # print(df.head())
        if (df.shape[0] > 0):
            print("df.iloc[0]['VGG-Face_cosine'] -> ", df.iloc[0]['VGG-Face_cosine'])
            if (df.iloc[0]['VGG-Face_cosine'] < 0.15):
                obj = DeepFace.analyze(img_path =img_path, actions=['age', 'gender', 'race', 'emotion'], enforce_detection=False)
                emotion_dict = obj['emotion']
                # print("emotion_dict: ", emotion_dict)
                
                identity = df.iloc[0].identity.split("\\")[1].split("/")[0]
                # print("identity: " , identity)
                json_predsDict = obj['emotion']
                emp_name_n_id = identity.split("-",1) # setting the maxsplit parameter to 1, will return a list with 2 elements!

                sorted_emotion_dict = dict(sorted(emotion_dict.items(), key = lambda x: x[1], reverse=True)) 
                # print("sorted_emotion_dict: ", sorted_emotion_dict)
                
                list_sorted_emotion_dict = list(sorted_emotion_dict)
                
                # Note: order of elif block is important here
                if list_sorted_emotion_dict[0] == "happy":
                    label = "LIKELY_HAPPY"
                elif (list_sorted_emotion_dict[0] == "neutral") and (list_sorted_emotion_dict[1] == "happy"):
                    label = "LIKELY_HAPPY"
                elif list_sorted_emotion_dict[0] == "surprise" and list_sorted_emotion_dict[1] == "happy":
                    label = "LIKELY_HAPPY" 
                elif list_sorted_emotion_dict[0] == "neutral" and list_sorted_emotion_dict[5] == "happy":
                    label = "LIKELY_NEUTRAL"
                else:
                    label = "LIKELY_NOT_HAPPY"
                    
                try:
                    # predsDict_ = json.dumps(json_predsDict, indent=4)
                    data_ = {
                        "emotion_scores": json_predsDict,
                        "date": img_capture_date,
                        "time": img_capture_time,
                        "emp_name": emp_name_n_id[0],
                        "emp_id": emp_name_n_id[1],
                        "overall_sentiment": label,
                        "device_id": img_capturing_device
                    }

                    data_ = json.dumps(data_, indent=4)

                    print ("data: ", data_)
                    r = requests.post(url = RAW_SENTI_API_URI, data = data_, headers = headers_)
                    print ("Return of post request", r.json())
                except Exception as e:
                    print ("Problem while making post request to url ", RAW_SENTI_API_URI, ", Problem: ", e)


        # return render_template('upload.html', filename=filename)
        res = str(df.head())
        return res
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/face_app/upload_for_training', methods=['POST'])
def upload_image_for_training():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    img_capture_time = request.form.get('current_time')
    img_capture_date = request.form.get('current_date')
    img_capture_datetime = request.form.get('current_datetime')
    img_capture_emp_name = request.form.get('emp_name')
    img_capture_emp_id = request.form.get('emp_id')
    print("img_capture_time", img_capture_time)
    print("img_capture_date", img_capture_date)
    print("img_capture_datetime", img_capture_datetime)
    print("img_capture_emp_name", img_capture_emp_name)
    print("img_capture_emp_id", img_capture_emp_id)
    img_capturing_device = request.form.get('device_id')
    print("img_capturing_device", img_capturing_device)
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        sub_folder_name = str(img_capture_emp_name) + "-" + str(img_capture_emp_id)
        img_path = app.config['DATASET_FOLDER']  + '/' + sub_folder_name
        Path(img_path).mkdir(parents=True, exist_ok=True)
        print('upload_image filename: ' + filename)
        file.save(os.path.join(img_path, filename))

        # return render_template('upload.html', filename=filename)
        return "success"
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploaded_files_for_recog/' + filename), code=301)



if __name__ == '__main__':

    app.debug = True
    # 0.0.0.0 means ???all IPv4 addresses on the local machine???
    app.run(host='0.0.0.0', port=8080, debug=True)

    # Quick test configuration. Please use proper Flask configuration options
    # in production settings, and use a separate file or environment variables
    # to manage the secret key!
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    
    
