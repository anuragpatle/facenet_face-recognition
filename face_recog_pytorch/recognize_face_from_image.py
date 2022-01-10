from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from torchvision import datasets
from torch.utils.data import DataLoader
from PIL import Image
import cv2
import time
import os


# initializing MTCNN and InceptionResnetV1
mtcnn0 = MTCNN(image_size=240, margin=0, keep_all=False,
               min_face_size=40)  # keep_all=False
mtcnn = MTCNN(image_size=240, margin=0, keep_all=True,
              min_face_size=40)  # keep_all=True
resnet = InceptionResnetV1(pretrained='vggface2').eval()
#! initializing MTCNN and InceptionResnetV1


# Using webcam recognize face
# loading data.pt file
load_data = torch.load('data.pt')
embedding_list = load_data[0]
name_list = load_data[1]

img = Image.open("./photos/virat.jpg")
img_cropped_list, prob_list = mtcnn(img, return_prob=True)

if img_cropped_list is not None:
    boxes, _ = mtcnn.detect(img)

    for i, prob in enumerate(prob_list):
        print("prob: ", prob)
        if prob > 0.90:
            emb = resnet(img_cropped_list[i].unsqueeze(0)).detach()

            dist_list = []  # list of matched distances, minimum distance is used to identify the person

            for idx, emb_db in enumerate(embedding_list):
                dist = torch.dist(emb, emb_db).item()
                dist_list.append(dist)

            min_dist = min(dist_list)  # get minumum dist value
            min_dist_idx = dist_list.index(
                min_dist)  # get minumum dist index
            # get name corrosponding to minimum dist
            name = name_list[min_dist_idx]

            box = boxes[i]

            print("name: ", name)
