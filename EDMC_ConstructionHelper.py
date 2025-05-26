"""
EDMC Construction Helper class
"""
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
# ---- EDMC logger setup ----
import logging
import os
try:
    from config import appname, config
    
    plugin_name = os.path.basename(os.path.dirname(__file__))
    logger = logging.getLogger(f'{appname}.{plugin_name}')
    # The logger should have been set up by the EDMC core
    if not logger.hasHandlers():
        print("I thought this wouldn't happen again in current version of EDMC!")
except ModuleNotFoundError:
    # We are not running from EDMC
    logger = logging.getLogger(__name__)
    config = False

# ---- EDMC logger setup end ----
   
class ConstructionHelper():
    def __init__(self, plugin_dir):
        # the "Name" of this plugin that is used to differentiate it
        # from other plugins
        self.Prefix = 'ConstructionHelper'
 
        # -------- Configuration (may get a gui) --------
        # display the goods sorted by category (True) or alphabetic (False)
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

        # maximum height of the site selection listbox
        self.config_listboxHeight = 4
        # minimum width on the site selection listbox in "characters"
        self.config_listboxWidth = 35
        # option to set the BG color of the listbox
        #  until I figure out how to use the EMDC UI theme
        #  uncomment the line with 'grey4' to use the dark-theme background color
        self.config_listboxBG = False
        # self.config_listboxBG = 'grey4'

        # maximum number of station economies to display:
        self.config_max_economies = 6
        # -------- Internal data structures --------
        self.SiteNames = {}
        self.GoodsRequired = {}
        self.goods_string = tk.StringVar()
        self.values_string = tk.StringVar()
        self.listbox_items = tk.StringVar()
        self.station_economy = tk.StringVar()
        self.listbox_IDs = []
        self.listbox_stations = []
        self.get_config()
        self.set_config()

    def get_config(self):
        if config:
            # these default to 0 either way
            self.config_overlayX = config.get_int(self.Prefix+"overlayX")
            self.config_overlayY = config.get_int(self.Prefix+"overlayY")
            self.config_fontSize = config.get_int(self.Prefix+"fontSize")
            # set these only if set
            if config.get_str(self.Prefix+"overlayFG"):
                self.config_overlayFG = config.get_str(self.Prefix+"overlayFG")
            if config.get_str(self.Prefix+"overlayFG"):
                self.config_overlayBG = config.get_str(self.Prefix+"overlayBG")
            if config.get_int(self.Prefix+"Alpha"):                
                self.config_Alpha = config.get_int(self.Prefix+"Alpha")/100.

    def set_config(self):
        if config:
           config.set(self.Prefix+"overlayX", self.config_overlayX)
           config.set(self.Prefix+"overlayY", self.config_overlayY)
           config.set(self.Prefix+"fontSize", self.config_fontSize)
           config.set(self.Prefix+"overlayFG", self.config_overlayFG)
           config.set(self.Prefix+"overlayBG", self.config_overlayBG)
           config.set(self.Prefix+"Alpha", int(self.config_Alpha*100))

    def UpdateStations(self,entry):
        if ('MarketID' not in entry):
            return
        if ((entry['MarketID'] not in self.SiteNames) or
            ('StationType' not in self.SiteNames[entry['MarketID']])):
            update_list = False
            if (entry['MarketID'] in self.SiteNames):
                update_list = True
            self.SiteNames[entry['MarketID']] = {};
            self.SiteNames[entry['MarketID']]['StationName']=entry['StationName']
            self.SiteNames[entry['MarketID']]['StationType']=entry['StationType']
            self.SiteNames[entry['MarketID']]['System']=entry['StarSystem']
            #self.SiteNames[entry['MarketID']]['']=entry['']
            if 'StationName_Localised' in entry:
                self.SiteNames[entry['MarketID']]['StationName_Localised'] = entry['StationName_Localised']
            self.SiteNames[entry['MarketID']]['Name'] = self.GetShortStationName(entry['MarketID'])
            if update_list:
                self.update_listbox()
        self.UpdateEconomy(entry)

    def GetShortStationName(self,MarketID):
        Name = ""
        # Name for System colonization ship
        if ((self.SiteNames[MarketID]['StationType'] == 'SurfaceStation') and
            (self.SiteNames[MarketID]['StationName'].split(';')[0] == '$EXT_PANEL_ColonisationShip')):
            Name = self.SiteNames[MarketID]['System']+": Primary Port"
        elif (self.SiteNames[MarketID]['StationType'] == 'SpaceConstructionDepot'):
            Name = self.SiteNames[MarketID]['System']+": Orbital Site"+ self.SiteNames[MarketID]['StationName'].split(':')[1]
        elif (self.SiteNames[MarketID]['StationType'] == 'PlanetaryConstructionDepot'):
            Name = self.SiteNames[MarketID]['System']+": Planetary Site"+ self.SiteNames[MarketID]['StationName'].split(':')[1]
        elif ('StationName_Localised' in self.SiteNames[MarketID]):
            Name = self.SiteNames[MarketID]['System']+": "+self.SiteNames[MarketID]['StationName_Localised']
        else:
            Name = self.SiteNames[MarketID]['System']+": "+self.SiteNames[MarketID]['StationName']
        return Name
                
    def UpdateGoods(self,entry,System="",StationName=""):
        if (entry['ConstructionComplete'] == False and
            entry['ConstructionFailed'] == False):
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
                    self.SiteNames[entry['MarketID']] = {}
                    self.SiteNames[entry['MarketID']]['StationName'] = StationName
                    self.SiteNames[entry['MarketID']]['System'] = System
                    self.SiteNames[entry['MarketID']]['Name'] = StationName
                #print("\nUpdated  resources required for Market:",self.SiteNames[entry['MarketID']]['Name'])
            if entry['MarketID'] not in self.listbox_IDs:
                self.update_listbox(clear=True)
                idx = self.listbox_IDs.index(entry['MarketID'])
                self.gui_listbox.selection_set(idx)
            self.update_values()
        else: #Construction is either complete or has failed
            if entry['MarketID'] in self.GoodsRequired:
                self.GoodsRequired.pop(entry['MarketID'])
                self.update_listbox()
                self.update_values()

    def UpdateEconomy(self,entry):
        """
        "StationEconomies":[ { "Name":"$economy_HighTech;", "Name_Localised":"High Tech", "Proportion":2.300000 }, { "Name":"$economy_Military;", "Name_Localised":"Military", "Proportion":0.400000 } ]
        """        
        if "StationEconomies" in entry:
            proportion_sum = 0.
            econ_names = []
            econ_prop = []
            for econ_dict in entry["StationEconomies"]:
                if econ_dict["Name"] == "$economy_Agri;":
                    econ_names.append(" Agr:{0:.1f}%")
                elif econ_dict["Name"] == "$economy_Extraction;":
                    econ_names.append(" Ext:{0:.1f}%")
                elif econ_dict["Name"] == "$economy_Industrial;":
                    econ_names.append(" Ind:{0:.1f}%")
                elif econ_dict["Name"] == "$economy_HighTech;":
                    econ_names.append(" HT:{0:.1f}%")
                elif econ_dict["Name"] == "$economy_Military;":
                    econ_names.append(" Mil:{0:.1f}%")
                elif econ_dict["Name"] == "$economy_Refinery;":
                    econ_names.append(" Ref:{0:.1f}%")
                elif econ_dict["Name"] == "$economy_Tourism;":
                    econ_names.append(" Tour:{0:.1f}%")
                elif econ_dict["Name"] == "$economy_Terraforming;":
                    econ_names.append(" Ter:{0:.1f}%")
                elif econ_dict["Name"] == "$economy_Service;":
                    econ_names.append(" Serv:{0:.1f}%")
                elif econ_dict["Name"] == "$economy_Carrier;":
                    econ_names.append(" Carrier:{0:.1f}%")
                elif econ_dict["Name"] == "$economy_Colony;":
                    econ_names.append(" Col:{0:.1f}%")
                else:
                    econ_names.append("Unk:")
                econ_prop.append(float(econ_dict["Proportion"]))
                proportion_sum += float(econ_dict["Proportion"])
            economy_string = "=> " +self.SiteNames[entry['MarketID']]['Name'] + "\n==>"
            for ind in range(len(econ_names)):
                if ind > 0:
                    economy_string += ','
                if ind < self.config_max_economies:
                    economy_string += econ_names[ind].format(econ_prop[ind]/proportion_sum*100.)
                elif ind == self.config_max_economies:
                    economy_string += ' +'
            self.station_economy.set(economy_string)
        return

                
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
            fontObj = tkFont.Font(size=self.config_fontSize)
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
        self.gui_button_close.grid(column=0,row=2,columnspan=3,sticky=(tk.E,tk.W))

    def close_overlay(self):
        self.gui_overlay.destroy()
        self.gui_button_open.grid(column=0,row=2,columnspan=3,sticky=(tk.E,tk.W))
        self.gui_button_close.grid_remove()
 
    def init_gui(self,parent):
        self.parent = parent
        self.gui_frame = tk.Frame(parent, borderwidth=0)
        self.gui_frame.grid(sticky=(tk.E,tk.W,tk.N,tk.S))

        self.gui_listbox = tk.Listbox(self.gui_frame, listvariable=self.listbox_items,
                                      selectmode=tk.EXTENDED, exportselection=False,
                                      height=1, width=self.config_listboxWidth);
        self.gui_listbox.bind("<<ListboxSelect>>",self.update_values)
        if self.config_listboxBG:
            self.gui_listbox.configure(background=self.config_listboxBG)
        self.gui_scrollbar = tk.Scrollbar(self.gui_frame, orient=tk.VERTICAL,
                                          command=self.gui_listbox.yview)
        self.gui_listbox.configure(yscrollcommand=self.gui_scrollbar.set)
        self.gui_listbox.grid(column=0,row=0,columnspan=2,sticky=(tk.W,tk.E,tk.N,tk.S))
        self.gui_scrollbar.grid(column=2,row=0,sticky=(tk.N,tk.S))
        
        self.gui_goods = tk.Label(self.gui_frame, textvariable=self.goods_string,
                                  justify=tk.RIGHT)
        self.gui_values = tk.Label(self.gui_frame, textvariable=self.values_string,
                                   justify=tk.LEFT)
        self.gui_goods.grid(column=0,row=1,sticky=(tk.E))
        self.gui_values.grid(column=1,row=1,sticky=(tk.W))

        self.gui_button_open = tk.Button(self.gui_frame,text="Open overlay",
                                          command=self.open_overlay)
        self.gui_button_open.grid(column=0,row=2,columnspan=3,sticky=(tk.E,tk.W))
        self.gui_button_close = tk.Button(self.gui_frame,text="Close overlay",
                                          command=self.close_overlay)
        self.gui_button_close.grid_remove()
        self.gui_frame.grid_columnconfigure(0, weight=1)
        self.gui_frame.grid_columnconfigure(1, weight=1)
        self.gui_economies = tk.Label(self.gui_frame, textvariable=self.station_economy,
                                      justify=tk.LEFT )
        self.gui_economies.grid(column=0,row=3,columnspan=3,sticky=(tk.W))

        self.update_listbox()
        self.update_values()
        
        return self.gui_frame
    
    def update_listbox(self,clear=False):
        # if we don't know of any construction projects then clear out the listbox and display
        if len(self.GoodsRequired) == 0:
            self.listbox_items.set(['No known construction site'])
            self.gui_listbox.config(height=1)
            self.gui_listbox.selection_clear(0)
            self.goods_string.set('')
            self.values_string.set('')
            self.listbox_IDs = []
            self.listbox_stations = []
            return
        # we do know about construction projects
        # rebuild the listbox, remember selection
        selectedIDs = []
        for idx in self.gui_listbox.curselection():
            if int(idx) < len(self.listbox_IDs):
                selectedIDs.append(self.listbox_IDs[int(idx)])
        self.listbox_IDs = []
        self.listbox_stations = []
        for MarketID in self.GoodsRequired.keys():
            self.listbox_IDs.append(MarketID)
            self.listbox_stations.append(self.SiteNames[MarketID]['Name'])
        self.listbox_items.set(self.listbox_stations)
        lbox_height = min(len(self.GoodsRequired),self.config_listboxHeight)
        self.gui_listbox.config(height=lbox_height)
        # clear selection
        self.gui_listbox.selection_clear(0,len(self.listbox_IDs))
        # reset selection
        if not clear:
            for MarketID in selectedIDs:
                # We may have just removed a previously selected entry from the listbox
                if MarketID in self.listbox_IDs:
                    idx = self.listbox_IDs.index(MarketID)
                    self.gui_listbox.selection_set(idx)

    def update_values(self,event=None):
        if len(self.listbox_IDs):
            #calculate the needed values
            current = {}
            for idx in self.gui_listbox.curselection():
                MarketID = self.listbox_IDs[int(idx)]
                for resource in self.GoodsRequired[MarketID].keys():
                    if resource not in current:
                        current[resource] = self.GoodsRequired[MarketID][resource]
                    else:
                        current[resource] += self.GoodsRequired[MarketID][resource]
            goods=""
            values=""
            keys_sorted = list(current.keys())
            keys_sorted.sort()
            for resource in keys_sorted:
                goods += resource+":\n"
                values += str(current[resource])+"\n"
            self.goods_string.set(goods[:-1])
            self.values_string.set(values[:-1])

            
