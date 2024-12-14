#!/usr/bin/env python
import PySimpleGUI as sg
import numpy as np
import pandas as pd
import os
import cv2
import ast
import json
import time
from opencv_draw_annotation import draw_bounding_box
from urllib.request import urlopen
import copy

import yaml
with open("config.yaml","r") as f:
    config = yaml.safe_load(f.read())




col11 = sg.Image(key='image')
Output = sg.Text()
Input = sg.Text()
Error = sg.Text()
Asset = sg.Text()

REMARK = ['Bent', 'Broken', 'Missing', 'Plant Overgrown', 'Paint Worn Off', 'Dirt', 'Not Working', 'Others']
# config["remarks"].sort()
# config["comment"].sort()

REMARK = config["remarks"]
COMMENT = config["comment"]



# col12 = [[sg.Text('ENTER VIDEO PATH')],

#          [sg.Text('Input video Path', size=(16, 1)), sg.InputText('', key='-IN-', size=(32, 1)), sg.FileBrowse()],
#          [sg.Text('Verified json Path', size=(16, 1)), sg.InputText('', key='JSON', size=(32, 1)), sg.FileBrowse()],
#          [sg.Button('Submit Video', size=(15, 1))],
#          [sg.Button('START', size=(15, 1)), sg.Button('STOP', size=(15, 1))],
#          [sg.Text('MODIFY MASTER')],

#          [sg.Button('Replace Image', size=(15, 1))],
#          [sg.Text('Current Asset: '), Asset],
#          [sg.Text('Change Frames')],

#          [sg.Button('Previous Frame', size=(15, 1)), sg.Button('Next Frame', size=(15, 1))],
#          [sg.Text('Change Assets')],
#          [sg.Button('Previous Asset', size=(15, 1)), sg.Button('Next Asset', size=(15, 1))],
#          [sg.Button('EXIT', size=(15, 1)), sg.Text('Frame no: '), Input],
#          [sg.Text('FINAL SUBMISSION')],
#          [sg.Button('Upload', size=(15, 1))],
#          [sg.Text(' '), Error]]

# layout = [[col11, sg.Frame(layout=col12, title='Details TO Enter')]]



        

    



def save_json(data, CSV):
    data.to_csv(CSV)



def load_json(CSV):
    f = open(CSV, "r")
    file = f.read()
    # print(file)
    data = eval(file)

    return data


# assets_list = [(x,i,j) for x in range(len())]

def final_verify(ip=None, json=None, stream=False,index=0):
    col11 = sg.Image(key='image')
    Output = sg.Text()
    Input = sg.Text()
    Error = sg.Text()
    Asset = sg.Text()
    comment = sg.Text()
    remark = sg.Text()
    total = sg.Text()
    far_asset = sg.Text()
    new_pos = sg.Text()
    # asset_no = sg.Text()
    col12 = [[sg.Text('ENTER VIDEO PATH')],

             [sg.Text('Index', size=(16, 1)), sg.InputText('', key='-IN-', size=(32, 1))],
             [sg.Text('Json Path', size=(16, 1)), sg.InputText('', key='JSON', size=(32, 1)), sg.FileBrowse()],
             [sg.Button('Submit', size=(15, 1))],
             [sg.Button('START', size=(15, 1)),total,],
             [sg.Text('MODIFY MASTER')],
             [sg.Text('Comment ', size=(18, 1)), sg.InputCombo([], size=(38, 60), key='comment')],
             [sg.Text('Remark ', size=(18, 1)), sg.InputCombo([], size=(38, 60), key='remark')],
             [sg.Button('Add Info', size=(15, 1))],
            #  [sg.Button('Replace Image', size=(15, 1)),sg.Button('Far Asset', size=(15, 1)),far_asset],
            #  [sg.InputCombo([], size=(15, 7), key='New Pos'),sg.Button('Update Pos', size=(15, 1)),new_pos],

             [sg.Text('Current Asset: '), Asset],
             [sg.Text('Remark: '), remark],
             [sg.Text('Comment: '), comment],
             # [sg.Text('total'),sg.Text('current')]
             [sg.Text('Change Frames')],

            #  [sg.Button('Previous Frame', size=(15, 1)), sg.Button('Next Frame', size=(15, 1))],
            #  [sg.Text('Change Assets')],
             [sg.Button('Previous Asset', size=(15, 1)), sg.Button('Next Asset', size=(15, 1))],
            #  [sg.Button('BACK', size=(15, 1)), sg.Text('Frame no: '), Input],
             [sg.Text('FINAL SUBMISSION')],
            #  [sg.Button('Upload', size=(15, 1))],
             [sg.Text(' '), Error]]
    if ip is not None:
        col12 = col12[4:]
    layout = [[col11, sg.Frame(layout=col12, title='Details TO Enter')]]
    
    window = sg.Window('Data Verification Toolbox',
                       layout, resizable=True, finalize=True, return_keyboard_events=True, use_default_focus=False)
    # window['comment'].update(values=COMMENT)
    # window['remark'].update(values=REMARK)
    

    window.finalize()
    # index = 0
    output_frame = 0
    prev_asset=""
    while True:
        event, values = window.read()
        # print(event,values)
        if event == 'BACK' or event == sg.WIN_CLOSED:
            window.close()

            return False,output_frame,index
            # break

    
        if event == 'Submit':
            # if ip is None:
            ip = values['-IN-']

            # if json is None:
            json = values['JSON']
        if event == "START":
                # print(json)
                data = pd.read_csv(json)
                index = int(ip)
                if "REMARK" not in data.columns:
                    data["REMARK"]=["-" for x in range(len(data))]
                    data["COMMENT"]=["-" for x in range(len(data))]
                stream=True
                total_assets = len(data)
                try:
                    data["bbox"]=data["bbox"].apply(eval)
                except:
                    pass
        
        if not stream:
            continue

        if event == "Next Asset" or event == 'Right:114' or event == "Right:39":
            index = min(index + 1, total_assets - 1)

        if event == 'Previous Asset'  or 'Left:' in event:
            index = max(0, index - 1)

        if event == "Add Info" or "Return" in event or event == "\r":
            print()
            data["COMMENT"][index] = values["comment"]
            data["REMARK"][index] = values["remark"]

            save_json(data, json)

        assets_name = data["db_asset_name"][index].replace("LEFT_","").replace("RIGHT_","")
        bbox = data["bbox"][index]
        # img_path = data["img_path"][index]
        # db_img_path
        img_path = data["db_img_path"][index]


        img_path = os.path.join("https://seekright.takeleap.in/SeekRight/",img_path)


        resp = urlopen(img_path )
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        img = cv2.imdecode(image, cv2.IMREAD_COLOR) # The image object

        
        # img = cv2.imread(img_path)
        # "https://seekright.takeleap.in/SeekRight/"





        draw_bounding_box(img, bbox, labels=[assets_name],
                            color='red',font_scale=2)
        
        if prev_asset!=assets_name:
            window['comment'].update(values=COMMENT[assets_name] if assets_name in COMMENT else COMMENT['default'])
            window['remark'].update(values=REMARK[assets_name] if assets_name in REMARK else REMARK['default'])
            prev_asset=assets_name


        comment.update(value=data["COMMENT"][index], text_color='Yellow')
        remark.update(value=data["REMARK"][index], text_color='Yellow')
        



        img =cv2.resize(img,(1280,720))
        total.update(value=f" Total :{total_assets}, Index : {index}")
        imgbytes = cv2.imencode('.png', img)[1].tobytes()  # ditto
            
        window['image'].update(data=imgbytes)

# /home/tl028/Downloads/101_data.csv











if __name__ == "__main__":
    final_verify()