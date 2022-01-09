import os
from flask import Flask, flash, request, redirect, url_for, session, render_template
from werkzeug.utils import secure_filename
from flask_session import Session
from deepface import DeepFace


UPLOAD_FOLDER = 'static/uploaded_files'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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


@app.route('/face_app/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    img_capture_time = request.form.get('current_time')
    img_capture_date = request.form.get('current_date')
    img_capture_datetime = request.form.get('current_datetime')
    print("img_capture_time", img_capture_time)
    print("img_capture_date", img_capture_date)
    print("img_capture_datetime", img_capture_datetime)
    img_capturing_device = request.form.get('device_id')
    print("img_capturing_device", img_capturing_device)
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')
        img_path = UPLOAD_FOLDER  + '/' + filename
        print('upload_image filename: ' + filename)
        obj = DeepFace.analyze(img_path =img_path, actions=['age', 'gender', 'race', 'emotion'], enforce_detection=False)
        print("obj: ", obj)
        # df = DeepFace.find(img_path = img_path, db_path = "./dataset1", enforce_detection=False)
        df = DeepFace.find(img_path = img_path, db_path = "./dataset1", enforce_detection=False)

        print(df.head())
        # return render_template('upload.html', filename=filename)
        return "success"
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploaded_files/' + filename), code=301)


if __name__ == '__main__':
    app.debug = True
    # 0.0.0.0 means “all IPv4 addresses on the local machine”
    app.run(host='0.0.0.0', port=8080, debug=True)

    # Quick test configuration. Please use proper Flask configuration options
    # in production settings, and use a separate file or environment variables
    # to manage the secret key!
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
