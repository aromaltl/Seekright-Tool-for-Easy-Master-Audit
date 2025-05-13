import os
import cv2
import numpy as np

from PIL import Image
import PIL
import requests
import cv2
import glob
import os
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import json
import pickle
def ResizeWithPadding(img):
    w, h = img.size
    if w>h:
        comp=w-h
        # new=PIL.Image.new(img.mode,(w,w),(125,125,125))
        new=PIL.Image.new(img.mode,(w,w),(0,0,0))
        new.paste(img,(0,int(comp//2)))
    elif w<h:
        comp=h-w
        # new=PIL.Image.new(img.mode,(h,h),(125,125,125))
        new=PIL.Image.new(img.mode,(h,h),(0,0,0))
        new.paste(img,(int(comp//2),0))
    else:
        new=img
        
    return new.resize((256,256))

class classifier(torch.nn.Module):
    def __init__(self):
        super(classifier, self).__init__()
        resnet34 = models.resnet34(pretrained=True)
        # resnet34.fc=torch.nn.Linear(in_features=512, out_features=35, bias=True)
        # resnet34.load_state_dict(torch.load('best.pt'),strict=True)
        resnet34.fc=torch.nn.Linear(in_features=512, out_features=40, bias=True)
        if not os.path.exists('best_1.pt'):
            os.system("wget https://takeleap.in/best_1.pt")

        resnet34.load_state_dict(torch.load('best_1.pt',map_location=torch.device("cpu")),strict=True)
        self.extr=torch.nn.Sequential(*[x for x in resnet34.children()][:-1])#.cuda()
    def forward(self, x):
        x = self.extr(x)
        return x

class feature_extractor:
    def __init__ (self,):
        self.model=classifier()
        self.model.eval()
        self.preprocess = transforms.Compose([
            ResizeWithPadding,
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
    def __call__ (self,image_p,):
        if type(image_p) is not str:
            img= cv2.cvtColor(image_p, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
        else:
            img = Image.open(image_p)
        img = self.preprocess(img)#.cuda()
        img = img.unsqueeze(0)
        with torch.no_grad():
            features = self.model(img)
        # return features.squeeze().cpu().numpy()
        return features.squeeze().numpy()
    
    
def getcomment(yaml_config):

    if  os.path.exists("subclassify/data.pkl"):
        with open('subclassify/data.pkl',"rb") as f:
            data = pickle.load(f)
    
        label = data['cls']
        for lbl in label:
            if lbl not in yaml_config['comment']:
                yaml_config['comment'][lbl]=[]


            for astname in set(label[lbl]):
                yaml_config['comment'][lbl].append(str(astname))

        # print(yaml_config)

    else:

        for x in glob.glob("subclassify/images/**/*.jpeg",recursive=True):
            lbl = os.path.basename(os.path.dirname(x))
            astname = os.path.basename(os.path.dirname(os.path.dirname(x)))
            if lbl not in yaml_config:
                yaml_config['comment'][lbl]=[]
            
            yaml_config['comment'][lbl].append(astname)
        


def getembeddings(fe ):
    if not os.path.exists("subclassify/data.pkl"):

        embedding={}
        label={}
        for x in glob.glob("subclassify/images/**/*.jpeg",recursive=True):
            lbl = os.path.basename(os.path.dirname(x))
            astname = os.path.basename(os.path.dirname(os.path.dirname(x)))
            emb = fe(x)
            if astname not in embedding:
                embedding[astname]=[]
                label[astname]=[]
            label[astname].append(lbl)
            embedding[astname].append(emb)
        for keys in embedding:
            embedding[keys] = np.array(embedding[keys])
            label[keys] = np.array(label[keys])
        # np.savez('subclassify/data.npz',**{"emb":embedding,"cls":label})
        with open('subclassify/data.pkl',"wb") as f:
            pickle.dump({"emb":embedding,"cls":label}, f)


        	

    else:
        # data= np.load('subclassify/data.npz',allow_pickle=  True)
        with open('subclassify/data.pkl',"rb") as f:
            data = pickle.load(f)
        
        embedding = data["emb"]
        label = data['cls']
        # print(embedding)

    return embedding, label


def classify(data,cap):
    # if type(cap) is str:
    #     cap = cv2.VideoCapture(cap)
    fe = feature_extractor()

    vector,class_n = getembeddings(fe )
	

    for x in data["Assets"]:
        asset_name = x[0].replace("RIGHT_","").replace("LEFT_","")
        
        if len(x[5][1])>1 or asset_name not in vector:
            continue
        cap.set(1,x[2])
        ret,img = cap.read()
        img=img[x[3][1]:x[4][1],x[3][0]:x[4][0]]
        y=fe(img).reshape(1,-1)
        i=np.argmin(np.sum(abs(vector[asset_name] - y),axis=-1))
        x[5][1]=class_n[asset_name][i]
        print(class_n[asset_name][i])



if __name__ == "__main__":
    final_json = "/home/tl028/Documents/Seekright-Tool-for-Easy-Master-Audit/2024_0703_082244_00006F_final.json"
    video_path = "/home/tl028/Documents/Seekright-Tool-for-Easy-Master-Audit/2024_0703_082244_00006F.MP4"

    cap =cv2.VideoCapture(video_path)
    with open(final_json,"r") as f:
        data = eval(f.read())
    cap = cv2.VideoCapture(video_path)
    classify(data,cap)




    

