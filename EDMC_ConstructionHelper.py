"""
EDMC Construction Helper class
"""
import tkinter as tk
from tkinter import ttk

class ConstructionHelper():
    def __init__(self, plugin_dir):

        # -------- Configuration (may get a gui) --------
        # display the goods sorted by category or unsorted (= usually alphabetic)
        self.config_sorted = False #not implemented yet
        #position of the overlay window on the screen
        self.config_overlayX = 0 #pixels right from top left corner
        self.config_overlayY = 0 #pixels down from top left corner
        #foregroung and background color of the overlay
        # needs to be a color understood by TK
        # ED orange is: "#d17a00"; ED blue is "#00abd2"
        self.config_overlayFG = "#00c0ff"
        self.config_overlayBG = "black"
        # Font size for the overlay, 0 == use default
        self.config_fontSize = 0
        #transparency of the overlay window (0.0=invisible, 1.0=intransparent)
        # doesn't work reliably on Linux
        self.config_Alpha = 0.7
        #Windows-only: make overlay background fully transparent
        self.config_BGtrans = False

        # -------- Internal data structures --------
        self.SiteNames = {}
        self.GoodsRequired = {}
        self.goods_string = tk.StringVar()
        self.values_string = tk.StringVar()

    def UpdateStations(self,entry):
        if (('MarketID' in entry) and
            (entry['MarketID'] not in self.SiteNames)):
            if 'StationName_Localised' in entry:
                StationName = entry['StationName_Localised']
            else:
                StationName = entry['StationName']
            self.SiteNames[entry['MarketID']] = [StationName,entry['StarSystem']]
        
    def UpdateGoods(self,entry):
        if (entry['ConstructionComplete'] == False and
            entry['ConstructionFailed'] == False
            ):
            current = {}
            for resource in entry['ResourcesRequired']:
                amount = resource['RequiredAmount'] - resource['ProvidedAmount']
                if (amount>0):
                    current[resource['Name_Localised']] = amount;
            if not current:
                print("\nMarket no complete or failed but no goods required for ID:",entry['MarketID'])
                return False
            if (entry['MarketID'] not in self.GoodsRequired or
                self.GoodsRequired[entry['MarketID']] != current ):
                # Goods required new or updated
                self.GoodsRequired[entry['MarketID']] = current
                if entry['MarketID'] not in self.SiteNames:
                    print("\n MarketID",entry['MarketID'],"not in list of table names")
                    return
                print("\nConstruction resources required for Market:",self.SiteNames[entry['MarketID']])
                goods=""
                values=""
                for resource in current:
                    print(resource,':',current[resource]);
                    goods += resource+":\n"
                    values += str(current[resource])+"\n"
                self.goods_string.set(goods[:-1])
                self.values_string.set(values[:-1])

                
    def open_overlay(self):
        self.gui_overlay = tk.Toplevel()
        self.gui_overlay.config(bg="black")
        self.gui_overlay.overrideredirect(True)
        self.gui_overlay.geometry("+%d+%d"%(self.config_overlayX,self.config_overlayY))
        self.gui_overlay.attributes("-topmost", 1)
        self.gui_overlay_goods = tk.Label(self.gui_overlay, textvariable=self.goods_string,
                                          justify=tk.RIGHT,
                                          fg=self.config_overlayFG,
                                          bg=self.config_overlayBG)
        self.gui_overlay_values = tk.Label(self.gui_overlay, textvariable=self.values_string,
                                           justify=tk.LEFT,
                                           fg=self.config_overlayFG,
                                           bg=self.config_overlayBG)
        if self.config_fontSize:
            fontObj = tk.font.Font(size=self.config_fontSize)
            self.gui_overlay_goods.config(font=fontObj)
            self.gui_overlay_values.config(font=fontObj)            
        self.gui_overlay_goods.grid(column=0,row=0,sticky=(tk.E))
        self.gui_overlay_values.grid(column=1,row=0,sticky=(tk.W))
        #wait for the window before setting transparency
        self.gui_overlay.wait_visibility(self.gui_overlay)
        if '-transparentcolor' in self.gui_overlay.attributes() and self.config_BGtrans:
            self.gui_overlay.attributes('-transparentcolor',self.config_overlayBG)
        self.gui_overlay.attributes("-alpha", self.config_Alpha)
        #change buttons on main window
        self.gui_button_open.grid_remove()
        self.gui_button_close.grid(column=0,row=2,columnspan=2,sticky=(tk.N))

    def close_overlay(self):
        self.gui_overlay.destroy()
        self.gui_button_open.grid(column=0,row=2,columnspan=2,sticky=(tk.N))
        self.gui_button_close.grid_remove()
 
    def init_gui(self,parent):
        self.parent = parent
        self.gui_frame = tk.Frame(parent, borderwidth=0)
        self.gui_frame.grid()

        self.goods_string.set("Empty:")
        self.values_string.set("0")
        
        self.gui_goods = tk.Label(self.gui_frame, textvariable=self.goods_string,
                                  justify=tk.RIGHT)
        self.gui_values = tk.Label(self.gui_frame, textvariable=self.values_string,
                                   justify=tk.LEFT)
        self.gui_goods.grid(column=0,row=1,sticky=(tk.E))
        self.gui_values.grid(column=1,row=1,sticky=(tk.W))

        self.gui_button_open = tk.Button(self.gui_frame,text="Open overlay",
                                          command=self.open_overlay)
        self.gui_button_open.grid(column=0,row=2,columnspan=2,sticky=(tk.N))
        self.gui_button_close = tk.Button(self.gui_frame,text="Close overlay",
                                          command=self.close_overlay)
        self.gui_button_close.grid_remove()
        
        return self.gui_frame

