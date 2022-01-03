import cv2
from pathlib import Path
import requests
import json
import os


# Rest api end points
ROOT_SENTI_API_URI = "http://20.102.100.20:5000/facial-senti-api"
NEW_EMP_SENTI_API_URI = ROOT_SENTI_API_URI + "/add_emp"
headers_ = {'Content-Type': 'application/json'}


def capture_headshots():
    # Ask name for the person
    first_name = input(
        "New face detected. \nPlease enter the first name of the person this face belongs to: ")
    first_name = first_name.strip()
    last_name = input("Please enter the last name: ")
    last_name = last_name.strip()

    name = first_name + "_" + last_name
    emp_id = input("Please enter employee id: ")
    images_dir_name = name + "-" + emp_id
    image_save_path = "dataset/" + images_dir_name
    Path(image_save_path).mkdir(parents=True, exist_ok=True)
    data_ = {"emp_id": emp_id, "emp_name": name}
    data_ = json.dumps(data_, indent=4)

    # r = requests.post(url=NEW_EMP_SENTI_API_URI, data=data_, headers=headers_)
    # print("Return of post request", r)

    cam = cv2.VideoCapture(1)

    cv2.namedWindow(
        "press space to take a photo or esc for crop, save and exit", cv2.WINDOW_NORMAL)
    cv2.resizeWindow(
        "press space to take a photo or esc for crop, save and exit", 500, 300)

    img_counter = 0

    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow(
            "press space to take a photo or esc for crop, save and exit", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            # SPACE pressed
            img_name = image_save_path + \
                "/image_{}.jpg".format(img_counter)
            cv2.imwrite(img_name, frame)
            print("{} written!".format(img_name))
            img_counter += 1

    cam.release()

    cv2.destroyAllWindows()

    crop_images_to_faces(image_save_path)


def crop_images_to_faces(save_path):

    cropped_image_save_path = save_path + "/cropped/"

    for filename in os.listdir(save_path):

        if filename.endswith(".jpg"):

            file_complete_name = save_path + "/" + filename

            _img = cv2.imread(file_complete_name)
            print("filenme: ", file_complete_name)

            gray = cv2.cvtColor(_img, cv2.COLOR_BGR2GRAY)

            faceCascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=3,
                minSize=(30, 30)
            )

            print("[INFO] Found {0} Faces.".format(len(faces)))

            for (x, y, w, h) in faces:
                cv2.rectangle(_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                roi_color = _img[y:y + h, x:x + w]
                print("[INFO] Object found. Saving locally.")
                cv2.imwrite(cropped_image_save_path +
                            (str(w) + str(h) + '_faces.jpg'), roi_color)
            else:
                continue


if __name__ == '__main__':
    capture_headshots()
