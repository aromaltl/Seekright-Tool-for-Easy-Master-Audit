
import PySimpleGUI as sg
import threading
import yaml
with open("template.yaml","r") as f:
    template = yaml.safe_load(f.read())
with open("config.yaml","r") as f:
    config = yaml.safe_load(f.read())
    
for x in template:
    if x not in config:
        config[x]=template[x]

def mainwindow():
    sg.theme('DarkBlue14')
    col11 = sg.Image(filename='seek.png', key='image')  # Coloumn 1 = Image view
    Output = sg.Text()
    Input = sg.Text()
    Error = sg.Text()
    col12 = [[sg.Text('ENTER VIDEO PATH')],
             # [sg.Slider(range=(0, 1000), default_value=0, size=(50, 10), orientation="h",enable_events=True, key="slider")],
             [sg.Text('Video Path', size=(12, 1)), sg.InputText('', key='-IN-', size=(38, 1)), sg.FileBrowse()],
             [sg.Text('Json Path', size=(12, 1)), sg.InputText('', key='CSV', size=(38, 1)), sg.FileBrowse()],
             [sg.Button('Submit Videos', size=(12, 1))],
             [sg.Text('VIDEO PLAY')],

             [sg.Button('PLAY', size=(12, 1))],
             [sg.Text('Frame No:', size=(12, 1)), sg.InputText('', key='skip', size=(38, 1)),sg.Button('Go', size=(6, 1))],
             
             [sg.Text('MODIFY MASTER')],
             [sg.Button('Divert', size=(12, 1))],
             [sg.Button('Add Data', size=(12, 1))],
             [sg.Button('Delete Data', size=(12, 1)), sg.InputCombo([], size=(40, 4), key='Delete_drop'),
              sg.Button('Select')],
             [sg.Text('NAVIGATE')],
             [sg.Button('START', size=(12, 1)), sg.Button('STOP', size=(12, 1)),sg.Button('RemoveAsset', size=(12, 1))],

             [sg.Button('PREVIOUS', size=(12, 1)), sg.Button('NEXT', size=(12, 1)),sg.InputCombo([], size=(12, 1), key='Removefr')],
             [sg.Button('Generate'), sg.Text('<-Generate final json', size=(35, 1))],
             [sg.Button('SAVE FRAME', size=(12, 1)), sg.Button('EXIT', size=(12, 1)), sg.Text('', key='text'), Output,
              sg.Text('Frame no: '), Input]]

    tab1 = [[col11, sg.Frame(layout=col12, title='Details TO Enter')],
        [sg.Slider(range=(0, 1000), default_value=0, size=(200, 5), tick_interval=500, orientation="h",
                   enable_events=True, key="slider")]]

    layout = [[sg.TabGroup([[sg.Tab('STEMA', tab1, tooltip='tip')]])]]

    window = sg.Window('Data Verification Toolbox',
                       layout, resizable=True, finalize=True, return_keyboard_events=True, use_default_focus=False)

    window.finalize()
    return window,Input

class AssetSelectWindow:
    def __init__(self,):
        self.asset_window = None
        self.selection = ''
        self.assets = set()
        self.asset_window2 = None
        self.linearassets = set(config["linear"])
        self.extrabuttons = [ [sg.Button(x, size=(15, 8),font=("Helvetica", 20, "bold") , pad=(0, 0)) for x in ("Start" ,"End", "None")] ]

    def create_asset_select_window(self,keys, cols,hide=True):
        '''
        creating window for asset selection
        
        '''
        layout = []
        for x in keys:
            self.assets.add(x.replace("_Start","").replace("_End",""))
        keys = list(self.assets)
        d = len(keys)
        r = d % cols
        keys = keys + [""] * (cols - r)
        n = len(keys) // cols
        
        for hh in range(n):
            
            layout.append([sg.Button(keys[x + hh * cols], size=(32, 1), pad=(0, 0)) for x in range(cols)])
        layout.append([sg.Button("SELECTALL", size=(32, 1),button_color='red', pad=(0, 0))])
        layout.append([sg.InputText('', key='New_Asset', size=(58, 1)) ,sg.Button('ADD_NEW_ASSET', size=(18, 1))])  # ,
        
        win = sg.Window("Select Asset", layout, resizable=True, keep_on_top=True, finalize=True, enable_close_attempted_event=True,
                        element_justification='c', return_keyboard_events=True)
        win2 = sg.Window("Select Asset", self.extrabuttons , resizable=True, keep_on_top=True, finalize=True, enable_close_attempted_event=True,
                    element_justification='c', return_keyboard_events=False)
        if hide:
            win2.hide()
            win.hide()
        
        self.asset_window =win
        self.asset_window2 =win2
        

    def asset_select_window(self,data):
        self.asset_window.UnHide()
        # self.asset_window2.UnHide()
        while True:
            column, val = self.asset_window.read()

            segment=val["New_Asset"].lower()
            for fil in self.assets :
                if segment in fil.lower():
                    self.asset_window[fil].Update(button_color="#da5872")
                else:
                    self.asset_window[fil].Update(button_color="#6a759b")
            
            if column == "ADD_NEW_ASSET":
                if val["New_Asset"] not in data:
                        
                    data[val["New_Asset"].replace("_Start","").replace("_End","")] = 9900
                    
                    self.assets.add(val["New_Asset"])
                    assetlist = list(self.assets)
                    assetlist.sort(key=lambda strings: strings.replace("Bad_",""))
                    self.create_asset_select_window(assetlist, 6,hide=False)
                    #self.asset_window.close()

            elif column  in self.assets or column == "-WINDOW CLOSE ATTEMPTED-" or column == "SELECTALL":
                for fil in self.assets :
                    self.asset_window[fil].Update(button_color="#6a759b")
                self.asset_window.hide()
                if column != "-WINDOW CLOSE ATTEMPTED-":
                    if column in self.linearassets:
                        self.asset_window2.UnHide()
                        start_end, _ = self.asset_window2.read()
                        self.asset_window2.hide()
                        ncolumn = f"{column}_{start_end}"
                        if ncolumn in data:
                            column=ncolumn 
                        
                    self.selection = column
                    return True  
                return False
    def close(self):
        self.asset_window.close()