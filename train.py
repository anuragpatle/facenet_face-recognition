# importing libraries

from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from torchvision import datasets
from torch.utils.data import DataLoader
from PIL import Image


# initializing MTCNN and InceptionResnetV1
mtcnn0 = MTCNN(image_size=240, margin=0, keep_all=False,
               min_face_size=40)  # keep_all=False
mtcnn = MTCNN(image_size=240, margin=0, keep_all=True,
              min_face_size=40)  # keep_all=True
resnet = InceptionResnetV1(pretrained='vggface2').eval()
#! initializing MTCNN and InceptionResnetV1


# Read data from folder
dataset = datasets.ImageFolder('photos')  # photos folder path
# accessing names of peoples from folder names
idx_to_class = {i: c for c, i in dataset.class_to_idx.items()}


def collate_fn(x):
    return x[0]


loader = DataLoader(dataset, collate_fn=collate_fn)

name_list = []  # list of names corrospoing to cropped photos
# list of embeding matrix after conversion from cropped faces to embedding matrix using resnet
embedding_list = []

for img, idx in loader:
    print("Embedding for idx: ", idx)
    face, prob = mtcnn0(img, return_prob=True)
    if face is not None and prob > 0.92:
        emb = resnet(face.unsqueeze(0))
        embedding_list.append(emb.detach())
        name_list.append(idx_to_class[idx])

# save data
data = [embedding_list, name_list]
print("Saving embeddings to data.pt file..")
torch.save(data, 'data.pt')  # saving data.pt file
#! Read data from folder
