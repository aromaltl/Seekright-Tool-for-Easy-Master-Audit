import cv2
import PySimpleGUI as sg
import json
import os
from opencv_draw_annotation import draw_bounding_box

import yaml
with open("config.yaml","r") as f:
    config = yaml.safe_load(f.read())

linears = set(config["linear"])
def converting_to_asset_format(data_json, total_frames):
    # try:
    #     print("converting_to_asset_format cpp started...")
    #     import convert 
    #     data = convert.convert_format(json.dumps(data_json),total_frames)
    #     data = json.loads(data)
    #     # print(data)
    #     print("converting_to_asset_format cpp ended!!")
    #     return data
    # except Exception as ex:
    #     print(f"Error in cpp convert convert:{ex}")

    data = {}
    print("converting_to_asset_format started...")
    for i in range(0, total_frames, 2):
        i = str(i)
        # print(i)
        if i not in data_json:
            continue

        for asset in data_json[i]:
            for index, v in enumerate(data_json[i][asset]):
                if asset not in data:
                    data[asset] = {}
                if asset in linears  and  int(v[0]) < 9000: # ignore linear which arenot manually added
                    continue
                if int(v[0]) not in data[asset]:
                    data[asset][int(v[0])] = []
                data[asset][int(v[0])].append([i, v[1], v[2]])
    print("converting_to_asset_format ended!!")
    return data


def generate(cap, data, video_name):
    video_name = os.path.basename(video_name).replace('.MP4', '')
    print("genearting images !!")
    os.makedirs(f"Upload_Images/{video_name}", exist_ok=True)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # float `width`
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    final_json = {"Assets": []}
    


    for asset in data:
        nth_last = config["det_loc"]["default"]
        print(asset)
        if 'Light' in asset:
            nth_last = config["det_loc"]['light_nth_last']
        if asset in config["det_loc"]:
            nth_last= config["det_loc"][asset]
        # val = data[asset][ids][0]
        for ids in data[asset]:
            if len(data[asset][ids])==0:
                continue
            val = data[asset][ids][0]
            for ijk in data[asset][ids][::-1]:
                # val=ijk
                if ijk[1][0]>15 and ijk[1][1]>15 and ijk[2][0]< width-15 and ijk[2][1] < height-15:
                    val=ijk
                    break
            # val = data[asset][ids][-min(nth_last, len(data[asset][ids]))]
            last = data[asset][ids][-1]

            if (val[1][0] + val[2][0]) / 2 > width / 2:
                Asset = "RIGHT_" + asset
            else:
                Asset = "LEFT_" + asset
            # print(ids)
            # name , id, frame , x1y1 , x2y2,[], frame_new
            push_meters = 10 if 'ight' in asset else 7
            final_json["Assets"].append([Asset, int(ids), int(val[0]), val[1], val[2], ['', ''], push_meters, int(last[0])])
            # cap.set(1, int(val[0]))
            # ret, frame = cap.read()
            # draw_bounding_box(frame, (val[1][0], val[1][1], val[2][0], val[2][1]), labels=[asset], color='green')
            # cv2.imwrite(f"Upload_Images/{video_name}/{video_name}_{str(val[0])}_{Asset}_{str(ids)}.jpeg", frame)
    print("images Done!!!")

    if os.path.exists(f"Upload_Images/{video_name}/{video_name}_final.json"):
        f1 = eval(open(f"Upload_Images/{video_name}/{video_name}_final.json", "r").read())
        for i, asset1 in enumerate(final_json["Assets"]):
            for asset2 in f1["Assets"]:
                # print(asset1,asset2)
                if asset1[:2] == asset2[:2]:
                    final_json["Assets"][i] = asset2
                    # cap.set(1, int(asset2[2]))
                    # ret, frame = cap.read()
                    # name=asset2[0].replace("RIGHT_","").replace("LEFT_","")
                    # draw_bounding_box(frame, (asset2[3][0], asset2[3][1], asset2[4][0], asset2[4][1]), labels=[name], color='green')
                    # os.remove(f"Upload_Images/{video_name}/{video_name}_{str(asset1[2])}_{asset1[0]}_{str(asset1[1])}.jpeg")
                    # cv2.imwrite(f"Upload_Images/{video_name}/{video_name}_{str(asset2[2])}_{asset2[0]}_{str(asset2[1])}.jpeg", frame)
                    break

    final_json["Assets"].sort(key=lambda yy: int(yy[2]))
    f = open(f"Upload_Images/{video_name}/{video_name}_final.json", "w")
    f.write(json.dumps(final_json))
    f.close()
    print("finished")


def confirmation(CONFIRMATION,data=None):
    Input = sg.Text(font=("Arial", 20), justification='center')
    layout = [[sg.Button("Confirm", size=(12, 2), pad=(50, 40), font=("Arial", 20)),
               sg.Button("Cancel", size=(12, 2), pad=(50, 40), font=("Arial", 20))], [Input]]
    # layout=sg.Column(layout, scrollable=True,  vertical_scroll_only=True)
    win = sg.Window(CONFIRMATION, layout, finalize=True, enable_close_attempted_event=True,
                    element_justification='c')
    
    if data is not None:
        for ast in data["flag"]:
            for side in data["flag"][ast]:
                if data["flag"][ast][side]%2==1:
                    Input.update(value=f"Not closed !!! >> {ast} {'Right' if side == 1 else 'Left' } !!!",text_color='Red')
                    # for x in range(total-1,-1,-1):

                    break
        
    else:
        Input.update(value=f"File looks good. Can i confirm ???")
    event = win.read()[0]
    win["Confirm"].update(disabled=True)
    win["Cancel"].update(disabled=True)
    win.read(timeout=0.1)
    # import time
    # time.sleep(4)
    if event == "Confirm":

        return True, win
    else:
        return False, win

# print(upload_confirmation())
