#!/usr/bin/env python

import numpy as np
import pandas as pd
import os
import cv2
import ast
import json
import time
import yaml


import yaml
with open("template.yaml","r") as f:
    template = yaml.safe_load(f.read())
with open("config.yaml","r") as f:
    config = yaml.safe_load(f.read())
    
for x in template:
    if x not in config:
        config[x]=template[x]



from upload import converting_to_asset_format, generate, confirmation
from final_submit import final_verify
from utils import mouse_call, extract_for_annotations, linear_data, addBBox, linear_remove, remove_left_lights
from utils import Task
import utils
from guiutils import AssetSelectWindow, mainwindow
"""
LAYOUT DESIGN
"""

# assets_list = ['LEFT_Signboard_Caution_Board', 'RIGHT_Signboard_Caution_Board', 'LEFT_Signboard_Chevron_Board', 'RIGHT_Signboard_Chevron_Board', 'LEFT_Signboard_Gantry_Board', 'RIGHT_Signboard_Gantry_Board', 'LEFT_Signboard_Hazard_board', 'RIGHT_Signboard_Hazard_board', 'LEFT_Signboard_Information_Board', 'RIGHT_Signboard_Information_Board', 'LEFT_Signboard_Mandatory_Board', 'RIGHT_Signboard_Mandatory_Board', 'LEFT_VMS_Gantry', 'RIGHT_VMS_Gantry', 'LEFT_Delineator', 'RIGHT_Delineator', 'LEFT_ECB_(SOS)', 'RIGHT_ECB_(SOS)', 'LEFT_Encroachment', 'RIGHT_Encroachment', 'LEFT_Hectometer_stone', 'RIGHT_Hectometer_stone', 'LEFT_Kilometer_Stone', 'RIGHT_Kilometer_Stone', 'LEFT_Solar_blinker', 'RIGHT_Solar_blinker', 'LEFT_Double_Arm_Street_Light', 'RIGHT_Double_Arm_Street_Light', 'LEFT_Pot_Holes', 'RIGHT_Pot_Holes', 'LEFT_Street_Light_Slanding', 'RIGHT_Street_Light_Slanding', 'LEFT_Single_Arm_Light_Slanting', 'RIGHT_Single_Arm_Light_Slanting', 'LEFT_High_Mast_Light', 'RIGHT_High_Mast_Light', 'Chainage']
global CSV

CSV = None
PLAY = True
# column = ''

# col11 = sg.Image(filename='bg2.png', key='image')  # Coloumn 1 = Image view
# Output = sg.Text()
# Input = sg.Text()
# Error = sg.Text()
# col12 = [[sg.Text('ENTER VIDEO PATH')],
#          # [sg.Slider(range=(0, 1000), default_value=0, size=(50, 10), orientation="h",enable_events=True, key="slider")],
#          [sg.Text('Input video Path', size=(18, 1)), sg.InputText('', key='-IN-', size=(38, 1)), sg.FileBrowse()],
#          [sg.Text('Normalized CSV File ', size=(18, 1)), sg.InputText('', key='CSV', size=(38, 1)), sg.FileBrowse()],
#          [sg.Button('Submit Videos')],
#          [sg.Text('VIDEO PLAY')],
#          [sg.Button('PLAY', size=(18, 1))],
#          [sg.Text('ENTER FRAME NUMBER TO JUMP IN')],
#          [sg.Text('Take Me To:', size=(18, 1)), sg.InputText('', key='skip', size=(38, 1))],
#          [sg.Button('Go', size=(18, 1))],
#          [sg.Text('MODIFY MASTER')],
#          # [sg.Button('Add Data', size=(15, 1)), sg.InputCombo([], size=(40,4), key='Coloumn'), sg.Button('Select1')],
#          [sg.Button('Add Data', size=(15, 1))],
#          [sg.Button('Delete Data', size=(15, 1)), sg.InputCombo([], size=(40, 4), key='Delete_drop'),
#           sg.Button('Select')],
#          [sg.Text('NAVIGATE')],
#          [sg.Button('START', size=(15, 1)), sg.Button('STOP', size=(15, 1))],

#          [sg.Button('PREVIOUS', size=(15, 1)), sg.Button('NEXT', size=(15, 1))],
#          [sg.Button('Generate'), sg.Text('<-Generate final json and images', size=(35, 1))],
#          [sg.Button('SAVE FRAME', size=(15, 1)), sg.Button('EXIT', size=(15, 1)), sg.Text('', key='text'), Output,
#           sg.Text('Frame no: '), Input]]




def save_json(data, CSV):
    '''
    save json 
    '''
    with open(CSV, "w") as outfile:
        json.dump(data, outfile)


#
# tab1 = [[col11, sg.Frame(layout=col12, title='Details TO Enter')],
#         [sg.Slider(range=(0, 1000), default_value=0, size=(200, 5), tick_interval=500, orientation="h",
#                    enable_events=True, key="slider")]]


def load_json(CSV):
    try:
        f = open(CSV, "r")
        file = f.read()
        data = json.loads(file)
    except Exception as ex:
        print(ex)
        data=eval(file)
    # data = eval(file)
    return data





def drop_down_list(frame, data):
    if str(frame) not in data:
        data[str(frame)] = {}

    i = []
    a = data[str(frame)]
    for x in a.keys():
        for c in a[x]:
            i.append([c[0], x])
    return i



def addtoJSON(frameNo, asset, bbox, data, id_):
    c = str(id_)
    if str(frameNo) not in data:
        data[str(frameNo)]={}
    try:
        data[str(frameNo)][asset].append([c, bbox[0], bbox[1]])

    except:
        data[str(frameNo)][asset] = [[c, bbox[0], bbox[1]]]


def verify(ip=None,CSV=None,output_frame=0,auto_start=None):
    column = ''
    PLAY = True
    window ,Input = mainwindow()

    Shift = False
    stream=False
    window_read = True
    # ip = ''
    SelectWindow = AssetSelectWindow()
    delete_val = ''
    while True:

        letter = None
       
        event_t, values_t = window.read(timeout= auto_start)
        
        if window_read:
            event, values  =  event_t, values_t
        
        # print()
        if event == 'slider':
            output_frame = int(int(values['slider']) // 2) * 2
            window['Delete_drop'].Update(values=drop_down_list(output_frame, data))

        text_elem = window['text']

        if len(event) == 1:
            print(ord(event))

            if ord(event) == 97 or ord(event) == 100 or ord(event) == 115:
                # print(ord(event))
                letter = ord(event)



        if event == 'EXIT' :# or event == sg.WIN_CLOSED:
            return "STOP"
        if event == 'Go' or (len(values['skip']) and ("Return" in event or event == "\r")):
            if int(values['skip']) % 2 == 0:
                output_frame = int(values['skip'])
                if str(output_frame) not in data:
                    data[str(output_frame)] = {}
            window['Delete_drop'].Update(values=drop_down_list(output_frame, data))
            window['skip'].Update('')
        # print(ip)
        if event == 'Submit Videos' or  auto_start:
            
            # if ip is None:
            #     ip = values['-IN-']
            # if CSV  is None:
            #     CSV = values['CSV']
            if len(values['-IN-']) > 4 :
                ip = values['-IN-']
            if  len(values['CSV']) > 4: 
                CSV = values['CSV']
            if CSV is not None:
                data = load_json(CSV)
            

        if event == 'START' or  auto_start:
            if len(ip) > 0 and len(CSV) > 0:
                print('START')
                cap = cv2.VideoCapture(str(ip))
                cap2 = cv2.VideoCapture(str(ip))
                
                os.makedirs("SavedImages",exist_ok=True)
                os.makedirs("DeletedImages",exist_ok=True)
                w,h=int(cap.get(3)), int(cap.get(4))
                vname = os.path.basename(ip).split(".")[0]
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                window["slider"].update(range=(0, total_frames - 1))
                if str(output_frame) not in data:
                    data[str(output_frame)] = {}
                    
                linear = linear_data(data,total_frames,w)
                lin = set(config["linear"])
                for x in set(config["fixed"]):
                    data[x] = data.get(x,9900)
                assets = []
                for x in data:
                    try:
                        x = int(x)
                    except:
                        assets.append(x)
                
                assets.sort(key=lambda strings: strings.replace("_End","").replace("Bad_","").replace("_Start",""))
                SelectWindow.create_asset_select_window(assets, 6)

                window['Delete_drop'].Update(values=drop_down_list(output_frame, data))

                stream = True
                run =  Task(CSV,cap,cap2,w,h,vname,total_frames,linear)
                save_json(data, CSV)



        if event == 'STOP':
            stream = False
            output_frame = 0
            SelectWindow.close()
            # ip = None
            # CSV = None
            img = cv2.imread('seek.png')
            imgbytes = cv2.imencode('.png', img)[1].tobytes()
            window['image'].update(data=imgbytes)

        auto_start=None
        

        if stream:

            if event == 'Add Data' or 'alt_l' in event.lower() or 'control_l' in event.lower() :
                
                if event == 'Add Data' or 'alt_l' in event.lower():
                    if not SelectWindow.asset_select_window(data):
                        continue         
                PREV_SELECTED_ASSET = SelectWindow.selection
                event = event if window_read else " "
                if len(PREV_SELECTED_ASSET) == 0: 
                    continue
                cap.set(cv2.CAP_PROP_POS_FRAMES, output_frame)
                utils.safe_open_window(windowname ='select the area')
                ret, frame = cap.read()
                if not ret:
                    frame =np.zeros((h,w,3),np.uint8)
                r = cv2.selectROI("select the area", frame)
                cv2.destroyWindow("select the area")
                if r[2] + r[3] < 10 :
                    continue
                #####################################
                data[PREV_SELECTED_ASSET] += 1
                BASE_PREV_SELECTED_ASSET = PREV_SELECTED_ASSET.replace("_Start","").replace("_End","")
                if BASE_PREV_SELECTED_ASSET in lin:
                    side = '1' if  (r[0]+(r[2]//2) ) > w//2 else '0'
                    
                    # if data["flag"][BASE_PREV_SELECTED_ASSET][side]==1: # only at end 
                    linear_remove(data,BASE_PREV_SELECTED_ASSET,side,output_frame,w)
                    if PREV_SELECTED_ASSET != BASE_PREV_SELECTED_ASSET:
                        data["flag"][BASE_PREV_SELECTED_ASSET][side]=(data["flag"][BASE_PREV_SELECTED_ASSET][side]+1)%2

                addtoJSON(output_frame, PREV_SELECTED_ASSET, [(r[0], r[1]), (r[2] + r[0], r[3] + r[1])], data,
                        data[PREV_SELECTED_ASSET])
                frame = addBBox(frame, output_frame, data)
                save_json(data, CSV)
                window['Delete_drop'].Update(values=drop_down_list(output_frame, data))

            if event == 'RemoveAsset':
                os.makedirs(f"DeletedImages/{vname}" ,exist_ok =True)
                for __ in range(10):
                    if not os.path.exists(f"DeletedImages/{vname}/{__}backup.json"):
                        save_json(data,f"DeletedImages/{vname}/{__}backup.json")
                        break

                if SelectWindow.asset_select_window(data):
                    lrfr=values['Removefr']
                    remove_left_lights(data,cap,SelectWindow.selection,lrfr,output_frame)
                  
                    save_json(data,CSV)
                    

            if event == 'SAVE FRAME' or letter == 83:
                ret = cap.set(cv2.CAP_PROP_POS_FRAMES, output_frame)
                ret, frame = cap.read()
                if not ret:
                    frame =np.zeros((h,w,3),np.uint8)
                frame = addBBox(frame, output_frame, data)
                cv2.imwrite("SavedImages/" + os.path.basename(ip) + '_' + str(output_frame) + '.jpeg', frame)

            if event == 'Select' or "Return" in event or event == "\r":
                delete_val = values['Delete_drop']

            if event == 'NEXT' or event == 'Right:114' or event == "Right:39":
                if Shift:
                    output_frame = int(output_frame) + 14
                    cap.set(1, output_frame)
                else:
                    output_frame = int(output_frame) + 2
                    cap.read()

                if str(output_frame) not in data:
                    data[str(output_frame)] = {}
                delete_val = ''
                window['Delete_drop'].Update(values=drop_down_list(output_frame, data))

            if event == 'PREVIOUS' or 'Left:' in event:

                output_frame = max(0, int(output_frame) - 14) if Shift else max(0, int(output_frame) - 2)
                if str(output_frame) not in data:
                    data[str(output_frame)] = {}
                delete_val = ''
                window['Delete_drop'].Update(values=drop_down_list(output_frame, data))
            if "Shift" in event:
                Shift = not Shift

            if event == "Generate":
                CONFIRM, wait = confirmation("Generate",data=data)
                if CONFIRM:
                    asset_format = converting_to_asset_format(data, total_frames)
                    generate(cap, asset_format, ip)
                    window.close()
                    wait.close()
                    return ip,CSV
                wait.close()

            # if (event == "Delete Data" or event == "Delete:119" or event == "\x7f" ) and len(delete_val):
            if event == "Divert":
                pass
                # run.break_linear(data,output_frame)


            if ("delete" in event.lower() or event == "\x7f") and len(delete_val):
                run.remove_asset(data,output_frame,delete_val)
                extract_for_annotations(cap2,output_frame,vname)

                save_json(data, CSV)
                delete_val = ""
                window['Delete_drop'].Update(values=drop_down_list(output_frame, data))

            if event == 'PLAY' or 'space:' in event.lower() and 'back' not in event.lower() or event == " ":  # backspace should not activate
                while True:
                    BRAKE, output_frame, temp,frame = run.opencv_gui(data,frame,output_frame,SelectWindow)
                    if not BRAKE :
                        
                        data[str(output_frame)]=temp
                        frame = addBBox(frame, output_frame, data)
                        save_json(data, CSV)
                        # output_frame-=2
                        # cap.set(1,output_frame)

                    else:
                        window['Delete_drop'].Update(values=drop_down_list(output_frame, data))
                        break
                cap.set(cv2.CAP_PROP_POS_FRAMES, output_frame)
                # cv2.destroyWindow("OUT")
            # output_frame = int(output_frame // 2) * 2
            if output_frame > total_frames - 1:
                cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
                output_frame = total_frames - 1
                output_frame = int(output_frame // 2) * 2
                window['Delete_drop'].Update(values=drop_down_list(output_frame, data))
                

            if event != 'NEXT' and 'Right:' not in event:
                ret = cap.set(cv2.CAP_PROP_POS_FRAMES, output_frame)
            ret, frame = cap.read()
            if not ret:
                frame =np.zeros((h,w,3),np.uint8)
            window["slider"].update(value=output_frame)
            Input.update(value=output_frame)
            frame = addBBox(frame, output_frame, data)

            frame = cv2.resize(frame, (1280, 720))
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()
            window['image'].update(data=imgbytes)
           



if __name__ == "__main__":
    ip,CSV = verify()


    Shift = False
    stream=False
    window_read = True
    # ip = ''

    breaker=True
    index=0
    while ip is not None:
        print(ip,CSV)
        v_name = os.path.basename(ip).replace(".MP4", "")
        final_json = f"Upload_Images/{v_name}/{v_name}_final.json"
        breaker,output_frame,index=  final_verify(ip, final_json,index=index)
        if breaker:
            break
        print("again going for verification")
        STOP = verify(ip=ip,CSV=CSV,output_frame=output_frame,auto_start=1)
        if STOP =="STOP":
            break
        
