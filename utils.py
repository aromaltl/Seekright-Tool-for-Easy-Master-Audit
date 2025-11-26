import cv2
import numpy as np
import yaml
import os
import time
from opencv_draw_annotation import draw_bounding_box
import json
import threading
lock = threading.Lock()
with open("template.yaml","r") as f:
    template = yaml.safe_load(f.read())
with open("config.yaml","r") as f:
    config = yaml.safe_load(f.read())
for x in template:
    if x not in config:
        config[x]=template[x]
lin = set(config["linear"])
def save_json(data, CSV):
    '''
    save json 
    '''
    with open(CSV, "w") as outfile:
        json.dump(data, outfile)


def safe_open_window(windowname):
    cv2.namedWindow(windowname, cv2.WND_PROP_FULLSCREEN)
    cv2.imshow(windowname,  np.zeros((300,300),np.uint8) )
    for ___ in range(15):
        cv2.waitKey(1)
    cv2.setWindowProperty(windowname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


def addasset(data,asset,ids,frameno,width,):
    newids = [ids[0]]+ids[1:]
    PREV_SELECTED_ASSET= asset
    data[PREV_SELECTED_ASSET] += 1
    data.setdefault(str(frameno), {}).setdefault(PREV_SELECTED_ASSET, [])
    newids[0] =str(data[PREV_SELECTED_ASSET])
    data[str(frameno)][PREV_SELECTED_ASSET].append(newids)

    BASE_PREV_SELECTED_ASSET = PREV_SELECTED_ASSET.replace("_Start","").replace("_End","")
    if BASE_PREV_SELECTED_ASSET in lin:
        side =  '1' if ((ids[1][0]+ids[2][0])//2) > width//2 else '0'
        
        linear_remove(data,BASE_PREV_SELECTED_ASSET,side,frameno,width)
        if PREV_SELECTED_ASSET != BASE_PREV_SELECTED_ASSET:
            data["flag"][BASE_PREV_SELECTED_ASSET][side]=(data["flag"][BASE_PREV_SELECTED_ASSET][side]+1)%2


def remove_left_lights(data,cap,column,lrfr,current_frame):
    width  = int(cap.get(3)//2)  # float `width`
    # total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    prevframe = int(lrfr[1:]) if not lrfr[0].isdigit() else int(lrfr)
    for x in range(current_frame,prevframe-1,-2):
        if x % 2 == 0:

            x = str(x)
            
            
            if x not in data:
                data[x] = {}

            if lrfr[0].isdigit():
                if column == "SELECTALL":
                    del data[x]
                elif column in data[x]:
                
                    del data[x][column]
            else:
                columns = data[x].keys() if column=="SELECTALL" else [column]
                
                for asset in columns:
                    if asset in data[x]:
                        temp = []
                        for yy in data[x][asset]:
                            
                            if ((yy[1][0]+yy[2][0])//2)>width and lrfr[0].lower() == 'l':
                                temp.append(yy)
                            if ((yy[1][0]+yy[2][0])//2)<width and lrfr[0].lower() == 'r':
                                temp.append(yy)
                            
                        data[x][asset] = temp
                        




def linear_remove(data,asset,side,st,w):
    '''
    remove linear assets till verified frame , 
    '''
    Base_Asset=asset.replace("_Start","_End")
    if Base_Asset not in set(config["linear"]):
        return None
    while st > -1:
        st-=2
        x=str(st)
        
        if x not in data :
            continue
        if Base_Asset not in data[x]:
            continue
        if '_End' in Base_Asset:
            if Base_Asset+"_Start" in data[x] and len(data[x][Base_Asset+"_Start"]):
                return None
            
        if "_Start" in Base_Asset:
            if Base_Asset+'_End' in data[x] and len(data[x][Base_Asset+'_End']):
                return None

        t=[]
        for ind,ids in enumerate(data[x][Base_Asset]):

            asset_side = '1' if ((ids[1][0]+ids[2][0])//2) > w//2  else '0'
            if asset_side != side or int(ids[0]) > 9000: # donot manually added and opposite side asset
                t.append(ids)
        data[x][Base_Asset]=t
        
        
    
try:
    import jetils
    addkeys = jetils.add_keys
except Exception as ex:
    print(ex)
    def addkeys(data,keys,val):
        temp = data
        found =True
        for x in keys:
            if x not in temp:
                temp[x]={}
                found = False
            tt = temp
            temp=temp[x]
        if not found:
            tt[keys[-1]]=val


# added
# def next_asset(cap,data,output_frame,total_frames,asset_seen,CSV):
#     '''
#     jump to next seen asset 
#     '''
#     for new_frames in range(output_frame,total_frames - 1,2):
#         if str(new_frames) not in data:
#             data[str(new_frames)] = {}
#         for ass in data[str(new_frames)]:
#             for items in data[str(new_frames)][ass]:
#                 if str(items[0]) + ass not in asset_seen:
#                     cap.set(1,new_frames-2)
#                     return new_frames-2

#     cap.set(1,int(total_frames/2)*2 - 2)
#     return int(total_frames/2)*2 - 2



if not config["draw_contours"] :      
    def addBBox(im, frameNo, data):
        if str(frameNo) not in data:
            data[str(frameNo)] = {}
        for ass in data[str(frameNo)]:
            for items in data[str(frameNo)][ass]:
                draw_bounding_box(im, (items[1][0], items[1][1], items[2][0], items[2][1]), labels=[items[0], ass],
                                color='green')
        return im   
else:
    def addBBox(im, frameNo, data):
        if str(frameNo) not in data:
            data[str(frameNo)] = {}
        for ass in data[str(frameNo)]:
            for items in data[str(frameNo)][ass]:
                draw_bounding_box(im, (items[1][0], items[1][1], items[2][0], items[2][1]), labels=[items[0], ass],
                                color='green')
                if len(items) > 3:
                    pts_np = np.array(items[3], dtype=np.int32).reshape((-1, 1, 2))
                    cv2.polylines(im, [pts_np], isClosed=True, color=(5, 10, 255), thickness=2)
        return im   




def linear_data(data,total_frames,width):
    lin = set(config["linear"])
    linear = {"asset":{}}
    for assets in lin:

        addkeys(data,("flag",assets,'0'),0)
        addkeys(data,("flag",assets,'1'),0)

        if assets not in data:
            data[assets]=9900
        if assets+"_Start" not in data:
            data[assets+"_Start"]=0
        if assets+"_End" not in data:
            data[assets+"_End"]=0

    for frame in range(0,total_frames,2):
        
        addkeys(data,[str(frame)],{})
        # if str(frame) not in data:
        #     data[str(frame)]={}
        for asset in data[str(frame)]:
            if asset not in lin:
                continue
            addkeys(linear["asset"],[asset],{})
            # if asset not in linear["asset"]:
            #     linear["asset"]={asset:{}}
            
            for ids in data[str(frame)][asset]:
                if int(ids[0]) < 9000: 
                    side =  '1' if ((ids[1][0]+ids[2][0])//2) > width//2 else '0'
                    addkeys(linear["asset"][asset],(ids[0],side),[frame,frame])
                    linear["asset"][asset][ids[0]][side][1]=frame
    import json
    with open("savvee.json", 'w') as file:
        json.dump(linear["asset"], file, indent=4)
    return linear
            
        

# def opencv_gui(cap,cap2,data,w,h,linear,CSV,vname,total_frames,frame,output_frame):
    
#     ret = True
#     PAUSE = True
#     asset_seen = set()
#     delay = 0.008 / config['speed']
#     play_size = config["play_size"]
#     lin = set(config["linear"])
#     cv2.namedWindow("OUT", cv2.WND_PROP_FULLSCREEN)
#     cv2.setWindowProperty("OUT", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
#     del_ast = mouse_call()
#     cv2.setMouseCallback('OUT',  del_ast.mclbk)
#     # cap.set(1,output_frame)
#     # ret,copy_frame=cap.read()
#     # cap.set(1,output_frame)
#     # h,w,_ = copy_frame.shape
#     delete_val =None
#     copy_frame=cv2.resize(frame,(w,h))

#     # cap.set(1, output_frame)
#     while True:
#         new_asset = False
#         window_read=True

#         if not PAUSE:
#             del_ast.ast=None
#             output_frame += 2
#             ret, frame = cap.read()
#             ret, frame = cap.read()
            
#             if not ret:
#                 break
#             copy_frame = frame.copy()
            
#             if str(output_frame) not in data:
#                 data[str(output_frame)] = {}

#             frame = addBBox(frame, output_frame, data)
#             # frame = addBBox(frame, output_frame, data)

#             for ass in data[str(output_frame)]:
#                 for ind,items in enumerate(data[str(output_frame)][ass]):
#                     if ass in lin and int(items[0]) < 9000:

#                         side =  1 if ((items[1][0]+items[2][0])//2) > w//2 else 0

#                         val_ue=linear["asset"].get(ass,{}).get(items[0],{}).get(side,[None,None])[data["flag"][ass][side]]
#                         # print(val_ue)

#                         temp_frame=copy_frame.copy()
#                         edge = "_End" if data["flag"][ass][side] else "_Start"
#                         if val_ue is not None and val_ue == output_frame:
#                             draw_bounding_box(temp_frame, (items[1][0], items[1][1], items[2][0], items[2][1]),
#                                 labels=[items[0], ass+edge],
#                                 color='#2419f9', border_thickness=3, )
                            
#                             cv2.imshow("OUT", temp_frame)
#                             key_press = cv2.waitKey(0) & 0xff
#                             if key_press == ord('y'):
#                                 # if data["flag"][ass][side] == 1 :
#                                 #     linear_remove(data,ass,side,output_frame,w)
#                                 linear_remove(data,ass,side,output_frame,w)
#                                 data["flag"][ass][side]=(data["flag"][ass][side]+1)%2
#                                 temp_data = data[str(output_frame)].copy()

#                                 data[ass+edge]+=1
#                                 drop_item=temp_data[ass].pop(ind)
#                                 drop_item[0]=str(data[ass+edge])
#                                 if ass+edge in temp_data:
#                                     temp_data[ass+edge].append(drop_item)
#                                 else:
#                                     temp_data[ass+edge]=[drop_item]

#                                 del del_ast
#                                 cv2.destroyWindow("OUT")
#                                 return False, output_frame, temp_data,frame
#                             if key_press == 27:
#                                 del del_ast

#                                 cv2.destroyWindow("OUT")
#                                 return True, output_frame, None,None

    
#                     else:          

#                         if str(items[0]) + ass not in asset_seen:
#                             asset_seen.add(str(items[0]) + ass)
#                             new_asset = True
#                             if "Start" not in ass and "_End" not in ass:
#                                 delete_val = items[0],ass
#                             draw_bounding_box(frame, (items[1][0], items[1][1], items[2][0], items[2][1]),
#                                                 labels=[items[0], ass],
#                                                 color='#c62424', border_thickness=3,)
#             frame = cv2.resize(frame, play_size)
#             cv2.imshow("OUT", frame)
#             time.sleep(delay)



#         elif del_ast.changed:
#             del_ast.update(data,output_frame,total_frames,cap2,vname)
#             frame=addBBox(copy_frame.copy(), output_frame, data)
#             frame = del_ast.highlight(frame)
#             del_ast.changed = False
#             save_json(data,CSV)
#             cv2.imshow("OUT", frame)
#         else:
#             if (frame.shape != copy_frame).any():
#                 # print(w,h,frame.shape, copy_frame)
#                 frame = cv2.resize(frame,(w,h))
#             cv2.imshow("OUT", frame)
        

#         key_press = cv2.waitKey(1) & 0xff

#         if key_press == ord(' ') or new_asset:
#             PAUSE = not PAUSE
#         if  key_press == ord('s'):
#             window_read=False
#             event = 'control_l'
#             break
#         if  key_press == ord('f') and delete_val is not None :
#             remove_asset(data,output_frame, total_frames,delete_val)
#             delete_val=None
#             PAUSE = not PAUSE
#             save_json(data,CSV)
            



#         if key_press == ord('w'):
#             PAUSE=False
#             output_frame=next_asset(cap,data,output_frame,asset_seen)
#         if key_press == 233:
#             window_read=False
#             event = 'alt_l'
#             break
#         if not ret or key_press == 27:
#             # del obj
#             break
#     del del_ast

#     cv2.destroyWindow("OUT")
#     return True, output_frame, None,None


def extract_for_annotations(cap,frame,vname):
    # total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    data={"Frames":set()}
    if os.path.exists(f"DeletedImages/{vname}_deleted.json"):
        with open(f"DeletedImages/{vname}_deleted.json",'r') as f:
            data = json.load(f)
        data["Frames"]=set(data["Frames"])

    for x in range(max(0,frame-18),frame+18,6):
        # cap.set(1,x)
        # ret,fra = cap.read()
        # if not ret:
        #     break 
        # cv2.imwrite(f"DeletedImages/{vname}_{x}.jpeg",fra)
        data["Frames"].add(x)
    data["Frames"] = list( data["Frames"])
    with open(f"DeletedImages/{vname}_deleted.json", 'w') as f:
        json.dump(data, f)





class mouse_call:
    def __init__(self,width,height,selection) :
        self.ast = None
        self.input =None
        self.changed=False
        self.video_size = width, height
        self.asset_select_window = selection
        

        # self.cap=cap
        # self.vname = vname

    def highlight(self,img):
        if self.ast is not None:
            items,_=self.ast
            img[int(items[1][1]): int(items[2][1]),int(items[1][0]): int(items[2][0]),2]=255
        return img

    def mclbk(self,event, x, y, flags,param):
        with lock:
            if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_MBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
                self.input=event,x,y
                self.changed = True ## Can cause dead lock donto


    def update(self,data,frameno,total_frames,cap,vname):
        if self.input_get() is None:
            return
        event,x,y= self.input_get()
        self.input_set(None)
        PREV_SELECTED_ASSET = ''
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.ast is None:
                for xx in data[str(frameno)]:
                    for id, yy in enumerate(data[str(frameno)][xx]):

                        if  int(yy[1][0]) <= x <= int(yy[2][0]) and int(yy[1][1]) <= y <= int(yy[2][1]):
                            self.ast = yy,xx
                            
                            self.changed_set(True)
                            break
            else:
                self.ast=None

        output_frame=frameno

        if (event == cv2.EVENT_MBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN)  and self.ast is not None:
            ids,asset = self.ast
            if "_End" in asset or  "_Start" in asset: ## update flag if manually added linear deleted
                side =  '1' if ((ids[1][0]+ids[2][0])//2) > self.video_size[0]//2 else '0'
                assetlin = asset.replace("_Start","").replace("_End","")
                data["flag"][assetlin][side]=(data["flag"][assetlin][side]+1)%2
                
            if event == cv2.EVENT_RBUTTONDOWN:
                if not self.asset_select_window.asset_select_window(data):
                    self.ast=None
                    return
                PREV_SELECTED_ASSET=self.asset_select_window.selection
                addasset(data,PREV_SELECTED_ASSET,ids,frameno,self.video_size[0])


            # delete_val = ids,asset
            delete_val = ((ids[0],ids[1:]),asset)
            found = 25
            extract_for_annotations(cap,output_frame,vname)

            RANGE=range(output_frame, total_frames)
            
            PREV_SELECTED_ASSET = '' if '_Start' in PREV_SELECTED_ASSET or '_End' in PREV_SELECTED_ASSET else PREV_SELECTED_ASSET
            for x in RANGE:
                if x % 2 == 1:
                    continue
                x = str(x)
                if x not in data:
                    data[x] = {}

                if delete_val[1] in data[x].keys():

                    for yy in range(len(data[x][delete_val[1]])):
                        if delete_val[0][0] == data[x][delete_val[1]][yy][0]:
                            deleted_asset = data[x][delete_val[1]].pop(yy)
                            
                            if PREV_SELECTED_ASSET and int(x)!=output_frame:
                                deleted_asset[0] = str(data[PREV_SELECTED_ASSET] )
                                data[x].setdefault(PREV_SELECTED_ASSET, []).append(deleted_asset)
                            found = 25
                            self.changed_set(True)
                            break
                found -= 1
                if found == 0:
                    break
            found = 25
            for x in range(output_frame - 1, -1, -1):
                if x % 2 == 1:
                    continue
                x = str(x)
                if x not in data:
                    data[x] = {}
                if delete_val[1] in data[x].keys():

                    for yy in range(len(data[x][delete_val[1]])):   
                        if delete_val[0][0] == data[x][delete_val[1]][yy][0]:
                            deleted_asset = data[x][delete_val[1]].pop(yy)
                            
                            if PREV_SELECTED_ASSET :
                                deleted_asset[0] = str(data[PREV_SELECTED_ASSET] )
                                data[x].setdefault(PREV_SELECTED_ASSET, []).append(deleted_asset)
                            found = 25
                            self.changed_set(True)
                            break
                found -= 1
                if found == 0:
                    break
            self.ast=None
    def changed_set(self,val):
        with lock:
            self.changed = val
    def changed_get(self):
        with lock:
            return self.changed
    def input_get(self):
        with lock:
            return self.input
    def input_set(self,val):
        with lock:
            self.input =val

# added to class



class Task:

    def __init__ (self,CSV,cap,cap2,w,h,vname,total_frames,linear):
        self.CSV = CSV
        self.cap = cap
        self.cap2 = cap2
        self.w = w 
        self.h = h
        self.vname  = vname
        self.total_frames = total_frames
        self.linear = linear
        self.asset_seen =set()
        
    

    def remove_asset(self, data,output_frame,delete_val):
        asset = delete_val[1]
        ids = delete_val[0]
        #todo:
        if "_End" in asset or  "Start" in asset: ## update flag if manually added linear deleted
            side =  '1' if ((ids[1][0]+ids[2][0])//2) > self.w//2 else '0'
            data["flag"][asset][side]=(data["flag"][asset][side]+1)%2


        found = 25
        for x in range(output_frame, self.total_frames):
            if x % 2 == 1:
                continue
            x = str(x)
            if x not in data:
                data[x] = {}

            if delete_val[1] in data[x]:

                for yy in range(len(data[x][delete_val[1]])):
                    if delete_val[0] == data[x][delete_val[1]][yy][0]:
                        data[x][delete_val[1]].pop(yy)
                        found = 25
                        break
            found -= 1
            if found == 0:
                break
        found = 25
        for x in range(output_frame - 1, -1, -1):
            if x % 2 == 1:
                continue
            x = str(x)
            if x not in data:
                data[x] = {}
            if delete_val[1] in data[x]:

                for yy in range(len(data[x][delete_val[1]])):
                    if delete_val[0] == data[x][delete_val[1]][yy][0]:
                        data[x][delete_val[1]].pop(yy)
                        found = 25
                        break
            found -= 1
            if found == 0:
                break


    def next_asset(self,data,output_frame):
        '''
        jump to next seen asset 
        '''
        for new_frames in range(output_frame,self.total_frames - 1,2):
            if str(new_frames) not in data:
                data[str(new_frames)] = {}
            for ass in data[str(new_frames)]:
                for items in data[str(new_frames)][ass]:
                    if str(items[0]) + ass not in self.asset_seen:
                        self.cap.set(1,new_frames-2)
                        return new_frames-2

        self.cap.set(1,int(self.total_frames/2)*2 - 2)
        return int(self.total_frames/2)*2 - 2


    def opencv_gui(self,data,frame,output_frame,Selection):
        
        ret = True
        PAUSE = True
        loading_firstime = True
        # asset_seen = set()
        delay = 0.008 / config['speed']
        play_size = config["play_size"]
        lin = set(config["linear"])

        safe_open_window('OUT')
        del_ast = mouse_call(self.w,self.h,Selection)
        cv2.setMouseCallback('OUT',  del_ast.mclbk)
        # self.cap.set(1,output_frame)
        # ret,copy_frame=self.cap.read()
        # cap.set(1,output_frame)
        # h,w,_ = copy_frame.shape
        delete_val =None
        # copy_frame=cv2.resize(frame,(self.w,self.h))

        # cap.set(1, output_frame)
        while True:

            new_asset = False
            window_read=True

            if not PAUSE or loading_firstime:
                del_ast.ast=None
                if not loading_firstime:
                    output_frame += 2
                    ret, frame = self.cap.read()
                    ret, frame = self.cap.read()

                else:
                    self.cap.set(1,output_frame)
                    ret,frame=self.cap.read()
                       
                if not ret:
                    break
                
                copy_frame = frame.copy()
                
                loading_firstime =False
                if str(output_frame) not in data:
                    data[str(output_frame)] = {}

                frame = addBBox(frame, output_frame, data)
                # frame = addBBox(frame, output_frame, data)

                for ass in data[str(output_frame)]:
                    for ind,items in enumerate(data[str(output_frame)][ass]):
                        if ass in lin and int(items[0]) < 9000:

                            side =  '1' if ((items[1][0]+items[2][0])//2) > self.w//2 else '0'

                            val_ue=self.linear["asset"].get(ass,{}).get(items[0],{}).get(side,[None,None])[data["flag"][ass][side]]
                            # print(val_ue)

                            temp_frame=copy_frame.copy()
                            edge = "_End" if data["flag"][ass][side]==1 else "_Start"

                            if val_ue is not None and val_ue == output_frame:
                                draw_bounding_box(temp_frame, (items[1][0], items[1][1], items[2][0], items[2][1]),
                                    labels=[items[0], ass+edge],
                                    color='#2419f9', border_thickness=3, )
                                
                                cv2.imshow("OUT", temp_frame)
                                key_press = cv2.waitKey(0) & 0xff
                                if key_press == ord('y'):
                                    # if data["flag"][ass][side] == 1 :
                                    #     linear_remove(data,ass,side,output_frame,w)
                                    linear_remove(data,ass,side,output_frame,self.w)
                                    data["flag"][ass][side]=(data["flag"][ass][side]+1)%2
                                    temp_data = data[str(output_frame)].copy()

                                    data[ass+edge]+=1
                                    drop_item=temp_data[ass].pop(ind)
                                    drop_item[0]=str(data[ass+edge])
                                    if ass+edge in temp_data:
                                        temp_data[ass+edge].append(drop_item)
                                    else:
                                        temp_data[ass+edge]=[drop_item]

                                    del del_ast
                                    self.asset_seen=set()
                                    cv2.destroyWindow("OUT")
                                    return False, output_frame, temp_data,frame
                                elif key_press == 27:
                                    del del_ast
                                    self.asset_seen=set()
                                    cv2.destroyWindow("OUT")
                                    return True, output_frame, None,None
                                # elif loading_firstime:
                                #     PAUSE = False

                        else:          

                            if str(items[0]) + ass not in self.asset_seen:
                                self.asset_seen.add(str(items[0]) + ass)
                                # new_asset = True
                                PAUSE =True
                                delete_val = items[0],ass
                                draw_bounding_box(frame, (items[1][0], items[1][1], items[2][0], items[2][1]),
                                                    labels=[items[0], ass],
                                                    color='#c62424', border_thickness=3,)
                
                frame = cv2.resize(frame, play_size)
                cv2.imshow("OUT", frame)
                time.sleep(delay)



            elif del_ast.changed_get():
                del_ast.update(data,output_frame,self.total_frames,self.cap2,self.vname)
                frame = addBBox(copy_frame.copy(), output_frame, data)
                frame = del_ast.highlight(frame)

                del_ast.changed_set(False)
                save_json(data,self.CSV)
                # frame = cv2.resize(frame, play_size)
                cv2.imshow("OUT", frame)
            else:
                # if (frame.shape != copy_frame).any():
                #     # print(w,h,frame.shape, copy_frame)
                #     frame = cv2.resize(frame,(self.w,self.h))
                # frame = cv2.resize(frame, play_size)
                cv2.imshow("OUT", frame)
            

            key_press = cv2.waitKey(1) & 0xff

            if key_press == ord(' ') :
                
                PAUSE = not PAUSE
            elif  key_press == ord('s'):
                window_read=False
                event = 'control_l'
                break
            elif  key_press == ord('f') and delete_val is not None :
                self.remove_asset(data,output_frame,delete_val)
                delete_val=None
                PAUSE = not PAUSE
                save_json(data,self.CSV)
            elif key_press == ord('y') and del_ast.ast:
                items,asset = del_ast.ast
                if asset in lin:
                    data[str(output_frame)][asset].remove(items)
                    side =  '1' if ((items[1][0]+items[2][0])//2) > self.w//2 else '0'
                    edge = "_End" if data["flag"][ass][side]==1 else "_Start"
                    asset = asset+edge
                
                addasset(data,asset ,ids =items,frameno=output_frame,width=self.w)
                frame=addBBox(copy_frame.copy(), output_frame, data)
                # frame = del_ast.highlight(frame)

                del_ast.ast =None
                save_json(data,self.CSV)
                # frame = cv2.resize(frame, play_size)
                cv2.imshow("OUT", frame)
            # if key_press == ord('r'):



            elif key_press == ord('w'):
                PAUSE=False
                output_frame=self.next_asset(data,output_frame)
            elif key_press == 233:
                window_read=False
                event = 'alt_l'
                break
            elif not ret or key_press == 27:
                # del obj

                break
        del del_ast
        self.asset_seen=set()
        cv2.destroyWindow("OUT")
        return True, output_frame, None,None
    
    def break_linear(self, data,output_frame):
        lin=set(config["linear"])
        for asset , value in data[output_frame].items():
            if asset in lin:
                for ids in value:
                    asset =asset.replace("_Start","").replace("_End","")
                    side =  '1' if ((ids[1][0]+ids[2][0])//2) > self.w//2 else '0'
                    
                    data["flag"][asset][side]=(data["flag"][asset][side]+1)%2


    def remove_asset(self,data,output_frame ,delete_val):

        # asset = delete_val[0]
        # ids = 
        # if "_End" in asset or  "Start" in asset: ## update flag if manually added linear deleted
        #     side =  1 if ((ids[1][0]+ids[2][0])//2) > self.video_size[0]//2 else 0
        #     data["flag"][asset][side]=(data["flag"][asset][side]+1)%2
        try:
            import jetils
            jetils.removeAsset( data,output_frame,delete_val[1],delete_val[0], self.total_frames)
            return

            
        except Exception as ex:
            print(ex)
            pass


        found = 30
        for x in range(output_frame, self.total_frames):
            if x % 2 == 1:
                continue
            x = str(x)
            if x not in data:
                data[x] = {}

            if delete_val[1] in data[x]:

                for yy in range(len(data[x][delete_val[1]])):
                    if delete_val[0] == data[x][delete_val[1]][yy][0]:
                        ids=data[x][delete_val[1]].pop(yy)
                        asset=delete_val[1]
                        if "_End" in asset or  "Start" in asset: ## update flag if manually added linear deleted
                            asset =asset.replace("_Start","").replace("_End","")
                            side =  '1' if ((ids[1][0]+ids[2][0])//2) > self.w//2 else '0'
                            data["flag"][asset][side]=(data["flag"][asset][side]+1)%2
                            return
                        found = 30
                        break
            found -= 1
            if found == 0:
                break
        found = 30
        for x in range(output_frame - 1, -1, -1):
            if x % 2 == 1:
                continue
            x = str(x)
            if x not in data:
                data[x] = {}
            if delete_val[1] in data[x]:

                for yy in range(len(data[x][delete_val[1]])):
                    if delete_val[0] == data[x][delete_val[1]][yy][0]:
                        data[x][delete_val[1]].pop(yy)
                        found = 30
                        break
            found -= 1
            if found == 0:
                break