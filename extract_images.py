import cv2
import os
import numpy as np

final_json = "/home/tl028/Documents/Seekright-Tool-for-Easy-Master-Audit/2024_0703_082244_00006F_final.json"
video_path = "/home/tl028/Documents/Seekright-Tool-for-Easy-Master-Audit/2024_0703_082244_00006F.MP4"

cap =cv2.VideoCapture(video_path)
with open(final_json,"r") as f:
    data = eval(f.read())
for ind ,x in enumerate(data["Assets"]):
    asset_name = x[0].replace("RIGHT_","").replace("LEFT_","")
    
    cap.set(1,x[2])
    ret,frame = cap.read()
    frame= frame[x[3][1]:x[4][1],x[3][0]:x[4][0]]
    sub = x[5][1]
    if len(x[5][1]) < 2:
        sub ="UNK" 
    os.makedirs(f"subclassify/images/{asset_name}/{sub}",exist_ok=True)
    cv2.imwrite(f"subclassify/images/{asset_name}/{sub}/{ind}.jpeg",frame)



