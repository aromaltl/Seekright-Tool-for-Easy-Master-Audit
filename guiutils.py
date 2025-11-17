
import PySimpleGUI as sg
class AssetSelectWindow:
    def __init__(self,):
        self.asset_window = None
        self.selection = ''
        self.assets = set()


    def create_asset_select_window(self,keys, cols,hide=True):
        '''
        creating window for asset selection
        
        '''
        layout = []

        d = len(keys)
        r = d % cols
        keys = keys + [""] * (cols - r)
        n = len(keys) // cols
        for x in keys:
            self.assets.add(x)
        for hh in range(n):
            
            layout.append([sg.Button(keys[x + hh * cols], size=(32, 1), pad=(0, 0)) for x in range(cols)])
        layout.append([sg.Button("SELECTALL", size=(32, 1),button_color='red', pad=(0, 0))])
        layout.append([sg.InputText('', key='New_Asset', size=(58, 1)) ,sg.Button('ADD_NEW_ASSET', size=(18, 1))])  # ,
        
        win = sg.Window("Select Asset", layout, resizable=True, keep_on_top=True, finalize=True, enable_close_attempted_event=True,
                        element_justification='c', return_keyboard_events=True)
        if hide:
            win.hide()
        
        self.asset_window =win
        

    def asset_select_window(self,data):
        self.asset_window.UnHide()
        while True:
            column, val = self.asset_window.read()
            segment=val["New_Asset"].lower()
            for fil in self.assets :
                if segment in fil.lower():
                    if "End" in fil:
                        self.asset_window[fil].Update(button_color="#A35060")
                    elif "Start" in fil:
                        self.asset_window[fil].Update(button_color="#D68393")
                    else:
                        self.asset_window[fil].Update(button_color="#cc6479")
                else:
                    self.asset_window[fil].Update(button_color="#6a759b")
            
            if column == "ADD_NEW_ASSET":
                data[val["New_Asset"]] = 9900
                self.asset_window.close()
                self.assets.append(val["New_Asset"])
                self.assets.sort(key=lambda strings: strings.replace("_End","").replace("Bad_","").replace("_Start",""))
                self.create_asset_select_window(self.assets, 6,hide=False)

            elif column  in self.assets or column == "-WINDOW CLOSE ATTEMPTED-" or column == "SELECTALL":
                for fil in self.assets :
                    self.asset_window[fil].Update(button_color="#6a759b")
                self.asset_window.hide()
                if column != "-WINDOW CLOSE ATTEMPTED-":
                    self.selection = column
                    return True  
                return False
    def close(self):
        self.asset_window.close()