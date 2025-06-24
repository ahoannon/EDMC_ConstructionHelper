"""
EDMC Construction Helper class
"""
import time, sys, shutil
import threading
import subprocess
import datetime as dt
from datetime import datetime
import json
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from tkinter import messagebox as mbox
import ftplib
from io import BytesIO
import ConstHelper_ContextMenu as ContextMenu
# ---- EDMC logger setup ----
import logging
import os
try:
    # import EDMC theme support
    from theme import theme
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
    theme = False

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
        # display the total number of tons needed
        self.show_total = True
        # display the economy composition of a station the user is docked to
        self.show_economy = True
        # normalize the economy composition before display
        self.show_economy_normalized = True
        
        # store site data to a local file 
        self.do_file_storage = False
        # if so, give the path to the file
        self.storage_file = ""
        # don't store data entries that are older than this (in seconds)
        self.storage_timeout = 604800 # 7 days

        # store data on remote ftp server
        self.do_ftp_storage = False
        # name of ftp-server
        self.ftp_server = ""
        # username on ftp-server
        self.ftp_user = ""
        # password on ftp-server
        self.ftp_password = ""
        # path to file on ftp-server
        self.ftp_filepath = ""
        # minimum time between ftp uploads
        self.ftp_upload_delay = 120
        # how many times (seconds) to (re)try sending if the worker thread is busy
        self.ftp_upload_retries = 10
        # minimum time between ftp downloads
        self.ftp_download_delay = 60
        # don't send data entries for non-tracked sites that are older than this (in seconds)
        self.untracked_timeout = 86400 # 24 hours

        
        # maximum height of the site selection listbox
        self.config_listboxHeight = 4
        # minimum width on the site selection listbox in "characters"
        self.config_listboxWidth = 35

        # maximum number of station economies to display:
        self.config_max_economies = 6

        # -------- Internal data structures --------
        self.SiteNames = {}
        self.GoodsRequired = {}
        self.DepotEventTimestamps = {}
        self.DepotEvents = {}
        self.goods_string = tk.StringVar()
        self.values_string = tk.StringVar()
        self.totals_string = tk.StringVar()
        self.listbox_items = tk.StringVar()
        self.station_economy = tk.StringVar()
        self.ftp_status = ""
        self.ftp_status_var = tk.StringVar()
        self.listbox_IDs = []
        self.listbox_stations = []
        self.last_ftp_upload = datetime(2025, 5, 26)
        self.last_ftp_download = datetime(2025, 5, 26)
        self.worker_thread = False
        self.worker_event = threading.Event()
        self.tmpwindow = False
        self.current = {}
        self.get_config()
        self.set_config()

        # -------- system dependent stuff --------
        if ((sys.platform == "linux" or sys.platform == "linux2") and
            (shutil.which('xclip') != None)):
            self.linux_with_xclip = True
        else:
            self.linux_with_xclip = False 


#---------- handle configuration
    def get_config(self):
        if config:
            try:
                if config.get_str(self.Prefix+"overlayX") != None:
                    self.config_overlayX = int(config.get_str(self.Prefix+"overlayX"))
                if config.get_bool(self.Prefix+"flushRight") != None:
                    self.flushRight = config.get_bool(self.Prefix+"flushRight")
                if config.get_str(self.Prefix+"overlayY") != None:
                    self.config_overlayY = int(config.get_str(self.Prefix+"overlayY"))
                if config.get_bool(self.Prefix+"flushBottom") != None:
                    self.flushBottom = config.get_bool(self.Prefix+"flushBottom")
                if config.get_str(self.Prefix+"fontSize") != None:
                    self.config_fontSize = int(config.get_str(self.Prefix+"fontSize"))
                if config.get_str(self.Prefix+"overlayFG") != None:
                    self.config_overlayFG = config.get_str(self.Prefix+"overlayFG")
                if config.get_str(self.Prefix+"overlayFG") != None:
                    self.config_overlayBG = config.get_str(self.Prefix+"overlayBG")
                if config.get_str(self.Prefix+"Alpha") != None:
                    self.config_Alpha = float(config.get_str(self.Prefix+"Alpha"))/100.
                if config.get_bool(self.Prefix+"ShowTotal") != None:
                    self.show_total = config.get_bool(self.Prefix+"ShowTotal")
                if config.get_bool(self.Prefix+"ShowEconomy") != None:
                    self.show_economy = config.get_bool(self.Prefix+"ShowEconomy")
                if config.get_bool(self.Prefix+"ShowEconomyNormalized") != None:
                    self.show_economy_normalized = config.get_bool(self.Prefix+"ShowEconomyNormalized")
                if config.get_bool(self.Prefix+"DoFile") != None:
                    self.do_file_storage = config.get_bool(self.Prefix+"DoFile")
                if config.get_str(self.Prefix+"storage_file") != None:
                    self.storage_file = config.get_str(self.Prefix+"storage_file")
                if config.get_bool(self.Prefix+"DoFTP") != None:
                    self.do_ftp_storage = config.get_bool(self.Prefix+"DoFTP")
                if config.get_str(self.Prefix+"FTPServer") != None:
                    self.ftp_server = config.get_str(self.Prefix+"FTPServer")
                if config.get_str(self.Prefix+"FTPUser") != None:
                    self.ftp_user = config.get_str(self.Prefix+"FTPUser")
                if config.get_str(self.Prefix+"FTPPasswd") != None:
                    self.ftp_password = config.get_str(self.Prefix+"FTPPasswd")
                if config.get_str(self.Prefix+"FTPFilePath") != None:
                    self.ftp_filepath = config.get_str(self.Prefix+"FTPFilePath")
            except ValueError:
                print("ValueError raised")
                pass
            if (self.do_ftp_storage and not (self.ftp_server and self.ftp_user and
                                             self.ftp_password and self.ftp_filepath)):
                print("FTP storage needs server, username, password, AND filename! \n"
                      " Deactivating FTP storage")
                self.do_ftp_storage = False

            
    def set_config(self):
        if config:
           config.set(self.Prefix+"overlayX", str(self.config_overlayX))
           config.set(self.Prefix+"flushRight", False)
           config.set(self.Prefix+"overlayY", str(self.config_overlayY))
           config.set(self.Prefix+"flushBottom", False)
           config.set(self.Prefix+"fontSize", str(self.config_fontSize))
           config.set(self.Prefix+"overlayFG", str(self.config_overlayFG))
           config.set(self.Prefix+"overlayBG", str(self.config_overlayBG))
           config.set(self.Prefix+"Alpha", str(int(self.config_Alpha*100)))
           config.set(self.Prefix+"ShowTotal", bool(self.show_total))
           config.set(self.Prefix+"ShowEconomy", bool(self.show_economy))
           config.set(self.Prefix+"ShowEconomyNormalized", bool(self.show_economy_normalized))
           config.set(self.Prefix+"DoFile", bool(self.do_file_storage))
           config.set(self.Prefix+"storage_file", str(self.storage_file))
           config.set(self.Prefix+"DoFTP", bool(self.do_ftp_storage))
           config.set(self.Prefix+"FTPServer", str(self.ftp_server))
           config.set(self.Prefix+"FTPUser", str(self.ftp_user))
           config.set(self.Prefix+"FTPPasswd", str(self.ftp_password))
           config.set(self.Prefix+"FTPFilePath", str(self.ftp_filepath))


#---------- handle station names
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

#---------- handle the resources and economy events
    def UpdateGoods(self,entry,System="Unknown System",StationName="Unknown Station"):
        #print("UpdateGoods called from:",threading.current_thread().name);
        # ignore older events
        newtime = datetime.strptime(entry['timestamp'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.UTC) 
        timediff = datetime.now(dt.UTC) - newtime
        if ( (timediff.total_seconds() > self.storage_timeout)  or
             (entry['MarketID'] in self.DepotEventTimestamps and
              newtime <=  self.DepotEventTimestamps[entry['MarketID']] )):
            #print("Ignored one event")
            self.worker_event.set()
            return
        # do a ftp-store if this is new and we aren't called from the worker
        if ((entry['MarketID'] not in self.GoodsRequired) and
            not (self.worker_thread and self.worker_thread.is_alive())):
            self.initiate_ftp_send()
        # process the entry
        # ToDo: store entries that the user manually de-selected 
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
                self.DepotEventTimestamps[entry['MarketID']] = newtime
                self.DepotEvents[entry['MarketID']] = entry
                if entry['MarketID'] not in self.SiteNames:
                    self.SiteNames[entry['MarketID']] = {}
                    self.SiteNames[entry['MarketID']]['StationName'] = StationName
                    self.SiteNames[entry['MarketID']]['System'] = System
                    self.SiteNames[entry['MarketID']]['Name'] = System+':'+StationName
                #print("\nUpdated  resources required for Market:",self.SiteNames[entry['MarketID']]['Name'])
                if entry['MarketID'] not in self.listbox_IDs:
                    self.update_listbox(clear=True)
                    idx = self.listbox_IDs.index(entry['MarketID'])
                    self.gui_listbox.selection_set(idx)
                self.update_values()
                self.save_data()
        else: #Construction is either complete or has failed
            self.DepotEventTimestamps[entry['MarketID']] = newtime
            self.DepotEvents[entry['MarketID']] = entry
            if entry['MarketID'] in self.GoodsRequired:
                self.GoodsRequired.pop(entry['MarketID'])
                self.update_listbox()
                self.update_values()
        #signal the worker that we are done (if needed)
        self.worker_event.set()

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
                    econ_names.append(" Agr:")
                elif econ_dict["Name"] == "$economy_Extraction;":
                    econ_names.append(" Ext:")
                elif econ_dict["Name"] == "$economy_Industrial;":
                    econ_names.append(" Ind:")
                elif econ_dict["Name"] == "$economy_HighTech;":
                    econ_names.append(" HT:")
                elif econ_dict["Name"] == "$economy_Military;":
                    econ_names.append(" Mil:")
                elif econ_dict["Name"] == "$economy_Refinery;":
                    econ_names.append(" Ref:")
                elif econ_dict["Name"] == "$economy_Tourism;":
                    econ_names.append(" Tour:")
                elif econ_dict["Name"] == "$economy_Terraforming;":
                    econ_names.append(" Ter:")
                elif econ_dict["Name"] == "$economy_Service;":
                    econ_names.append(" Serv:")
                elif econ_dict["Name"] == "$economy_Carrier;":
                    econ_names.append(" Carrier:")
                elif econ_dict["Name"] == "$economy_Colony;":
                    econ_names.append(" Col:")
                else:
                    econ_names.append("Unk:")
                econ_prop.append(float(econ_dict["Proportion"]))
                proportion_sum += float(econ_dict["Proportion"])
            economy_string = "=> " +self.SiteNames[entry['MarketID']]['Name'] + "\n==>"
            for ind in range(len(econ_names)):
                if ind > 0:
                    economy_string += ','
                if ind < self.config_max_economies:
                    economy_string += econ_names[ind]
                    if self.show_economy_normalized:
                        economy_string += "{0:.1f}%".format(econ_prop[ind]/proportion_sum*100.)
                    else:
                        economy_string += "{0:.0f}%".format(econ_prop[ind]*100.)
                elif ind == self.config_max_economies:
                    economy_string += ' +'
            self.station_economy.set(economy_string)
        return

#---------- handle the ftp store and retrieve events
    def initiate_ftp_send(self):
        if self.do_ftp_storage:
            tdiff = datetime.now() - self.last_ftp_upload
            if (tdiff.total_seconds() > self.ftp_upload_delay):
                #give it 100 ms to handle the incomming ConstructionDepot event then save to ftp.
                self.gui_frame.after(100,self.ftp_store)

    def initiate_ftp_get(self, entry):
        if self.do_ftp_storage:
            tdiff = datetime.now() - self.last_ftp_download
            if (tdiff.total_seconds() > self.ftp_download_delay):
                if ('StationType' in entry and
                    ((entry['StationType'] == "SpaceConstructionDepot") or
                     (entry['StationType'] == "PlanetaryConstructionDepot") or
                     (entry['StationName'].split(';')[0] == '$EXT_PANEL_ColonisationShip'))):
                    return
                self.ftp_get()

               
#---------- open and close the overlay window                
    def open_overlay(self):
        # Get screen dimensions in case we need them
        self.screen_width = self.gui_frame.winfo_screenwidth()
        self.screen_height = self.gui_frame.winfo_screenheight()
        # open the overlay
        self.gui_overlay = tk.Toplevel()
        self.gui_overlay.config(bg="black")
        self.gui_overlay.overrideredirect(True)
        #self.gui_overlay.geometry("+%d+%d"%(self.config_overlayX,self.config_overlayY))
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
        self.gui_button_close.grid(column=0,row=3,columnspan=3,sticky=(tk.E,tk.W))
        if (self.flushRight or self.flushBottom):
            self.gui_overlay.bind('<Configure>', self.position_overlay)
        else:
            self.position_overlay()
        
    def position_overlay(self, event=None):
        if self.flushRight:
            x_pos = self.screen_width - self.gui_overlay.winfo_width() + self.config_overlayX
        else:
            x_pos = self.config_overlayX
        if self.flushBottom:
            y_pos = self.screen_height - self.gui_overlay.winfo_height() + self.config_overlayY
        else:
            y_pos = self.config_overlayY
        self.gui_overlay.geometry("+%d+%d"%(x_pos,y_pos))
        
    def close_overlay(self):
        self.gui_overlay.destroy()
        self.gui_button_open.grid(column=0,row=3,columnspan=3,sticky=(tk.E,tk.W))
        self.gui_button_close.grid_remove()

#---------- handle event callbacks

    def remove_sites(self, ButtonPress=None):
        removeText = "Remove the following site(s)?\n"        
        for idx in self.gui_listbox.curselection():
            removeText += "- "+self.listbox_stations[idx]+"\n"
        result = mbox.askokcancel("Remove Sites", removeText,icon=mbox.WARNING)
        if result:
            for idx in self.gui_listbox.curselection():
                self.GoodsRequired.pop(self.listbox_IDs[idx])
            self.update_listbox()
            self.update_values()
            self.save_data()
        pass

    def mark_site_completed(self):
        indices = self.gui_listbox.curselection()
        if len(indices) != 1:
            mbox.showerror("Mark as Completed", "Please select exatly one site\n"
                           "to be marked as completed!",icon=mbox.ERROR)
            return
        removeText = "Mark the following site\n - " + self.listbox_stations[indices[0]]
        removeText += "\n as completed and remove it from the record?"
        result = mbox.askokcancel("Mark as Completed", removeText,icon=mbox.WARNING)
        if result:
            MarketID = self.listbox_IDs[indices[0]]
            self.DepotEventTimestamps[MarketID] = datetime.now(dt.UTC)
            entry = {'event' : 'ColonisationConstructionDepot'}
            entry['timestamp'] = datetime.now(dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
            entry['MarketID'] = MarketID
            entry['ConstructionComplete'] = False
            entry['ConstructionFailed'] = True
            self.DepotEvents[MarketID] = entry
            self.GoodsRequired.pop(MarketID)
            self.update_listbox()
            self.update_values()
            self.save_data()
        pass
           
    def clip_system_names(self, ButtonPress=None):
        #if ButtonPress: print("Called via hotkey",ButtonPress)
        clipstring = ""
        for idx in self.gui_listbox.curselection():
            MarketID = self.listbox_IDs[int(idx)]
            sysname = self.SiteNames[MarketID]['System']
            if (clipstring.find(sysname) == -1):
                if clipstring:
                    clipstring += ", "
                clipstring += sysname
        if self.linux_with_xclip:
            clipper = subprocess.Popen(["xclip", "-selection", "clipboard"],
                                       stdin=subprocess.PIPE)
            clipper.communicate(clipstring.encode('utf-8'))
        else:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(clipstring)
            self.parent.update()
        self.open_tmpwindow("Copied system(s)",1000)

    def clip_resources_spreadsheet(self, ButtonPress=None):
        clipstring = ""
        keys_sorted = list(self.current.keys())
        keys_sorted.sort()
        for resource in keys_sorted:
            clipstring +=  resource+"\t"
            clipstring += str(self.current[resource])+"\n"
        if not clipstring:
            self.open_tmpwindow("No needed resources.",3000)
        else:
            if self.linux_with_xclip:
                clipper = subprocess.Popen(["xclip", "-selection", "clipboard"],
                                           stdin=subprocess.PIPE)
                clipper.communicate(clipstring.encode('utf-8'))
            else:
                self.parent.clipboard_clear()
                self.parent.clipboard_append(clipstring)
                self.parent.update()
            self.open_tmpwindow("Copied resources for spreadsheet",1000)

            
    def open_tmpwindow(self, infotext="test", duration=1000):
        if not self.tmpwindow:
            self.tmpwindow = tk.Toplevel()
            self.tmpwindow.overrideredirect(True)
            posy = max(0,self.gui_frame.winfo_pointery()-20)
            self.tmpwindow.geometry("+%d+%d"%(self.gui_frame.winfo_pointerx(),posy))
            self.tmpwindow.attributes("-topmost", 1)
            tmplabel = tk.Label(self.tmpwindow,text=infotext)
            tmplabel.grid()
            self.tmpwindow.wait_visibility(self.tmpwindow)
            self.gui_frame.after(duration, self.destroy_tmpwindow)

            
    def destroy_tmpwindow(self):
        if self.tmpwindow:
            self.tmpwindow.destroy()
            self.tmpwindow = False
        

#---------- handle the general GUI
    def init_gui(self,parent):
        self.parent = parent
        self.gui_frame = tk.Frame(parent, borderwidth=0)
        self.gui_frame.grid(sticky=(tk.E,tk.W,tk.N,tk.S))

        self.gui_listbox = tk.Listbox(self.gui_frame, listvariable=self.listbox_items,
                                      selectmode=tk.EXTENDED, exportselection=False,
                                      height=1, width=self.config_listboxWidth);
        self.gui_listbox.bind("<<ListboxSelect>>",self.update_values)
        self.gui_listbox.bind("<Double-1>",self.remove_sites)
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
        self.gui_total_label =  tk.Label(self.gui_frame, text="Total:",
                                  justify=tk.RIGHT)
        self.gui_total_values = tk.Label(self.gui_frame, textvariable=self.totals_string,
                                   justify=tk.LEFT)
        #self.gui_total_label.grid(column=0,row=2,sticky=(tk.E))
        #self.gui_total_values.grid(column=1,row=2,sticky=(tk.W))
       
        self.gui_button_open = tk.Button(self.gui_frame,text="Open overlay",
                                          command=self.open_overlay)
        self.gui_button_open.grid(column=0,row=3,columnspan=3,sticky=(tk.E,tk.W))
        self.gui_button_close = tk.Button(self.gui_frame,text="Close overlay",
                                          command=self.close_overlay)
        self.gui_button_close.grid_remove()
        self.gui_frame.grid_columnconfigure(0, weight=1)
        self.gui_frame.grid_columnconfigure(1, weight=1)
        self.gui_economies = tk.Label(self.gui_frame, textvariable=self.station_economy,
                                      justify=tk.LEFT )
        #self.gui_economies.grid(column=0,row=4,columnspan=3,sticky=(tk.W))
        self.gui_ftp_status = tk.Label(self.gui_frame, textvariable=self.ftp_status_var,
                                       justify=tk.LEFT )
        fontObj = tkFont.Font(self.gui_ftp_status,self.gui_ftp_status.cget("font"))
        fontObj.configure(weight="bold")
        self.gui_ftp_status.configure(font=fontObj)

        self.gui_ftp_status.grid_remove()

        #set up the contex menu
        self.gui_listbox.focus_set()
        self.context_menus = ContextMenu.ContextMenus(self.gui_frame, self.gui_listbox, self)
        self.context_menus.add_labels_binding(self.gui_goods)
        self.context_menus.add_labels_binding(self.gui_values)
        self.context_menus.add_labels_binding(self.gui_total_label)
        self.context_menus.add_labels_binding(self.gui_total_values)
        self.gui_frame.bind("<Button-1>", self.context_menus.hide_context_menu) 
        self.gui_goods.bind("<Button-1>", self.context_menus.hide_context_menu) 
        self.gui_values.bind("<Button-1>", self.context_menus.hide_context_menu)
        self.gui_total_label.bind("<Button-1>", self.context_menus.hide_context_menu) 
        self.gui_total_values.bind("<Button-1>", self.context_menus.hide_context_menu) 
        self.gui_listbox.bind("<Control-Shift-C>", self.clip_system_names)
        
        self.update_listbox()
        self.update_values()
        # This is the very first time we start the worker, so don't need to check him
        self.worker_thread = threading.Thread(target=self.startup_data_retrieval, name="Worker")
        self.worker_thread.start()
        if theme:
            self.theme = theme.active
        #trigger a race condition
        ### only for debugging!!! ###
        #time.sleep(1)
        self.apply_gui_settings()
        return self.gui_frame

    def apply_gui_settings(self):
        #patched in theme support
        #ugly solution, needs to be imporved!
        if self.theme != theme.active:
            if theme.active > 0:
                self.gui_listbox.configure(background='grey4')
            else:
                self.gui_listbox.configure(background='white')
        self.theme = theme.active
        if self.show_economy:
            self.gui_economies.grid(column=0,row=4,columnspan=3,sticky=(tk.W))
        else:
            self.gui_economies.grid_remove()
        if self.show_total:
            self.gui_total_label.grid(column=0,row=2,sticky=(tk.E))
            self.gui_total_values.grid(column=1,row=2,sticky=(tk.W))
        else:
            self.gui_total_label.grid_remove()
            self.gui_total_values.grid_remove()
        self.ftp_status = ""
        self.update_ftp_status()

    def update_ftp_status(self):
        if self.ftp_status:
            self.ftp_status_var.set(self.ftp_status)
            self.gui_ftp_status.grid(column=0,row=4,columnspan=3,sticky=(tk.W))
        else:
            self.gui_ftp_status.grid_remove()
            
#---------- update the display
    def update_listbox(self,clear=False):
        # if we don't know of any construction projects then clear out the listbox and display
        if len(self.GoodsRequired) == 0:
            self.listbox_items.set(['No known construction site'])
            self.gui_listbox.config(height=1)
            self.gui_scrollbar.grid_remove()
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
        IDs = []
        stations = []
        for MarketID in self.GoodsRequired.keys():
            #self.listbox_IDs.append(MarketID)
            #self.listbox_stations.append(self.SiteNames[MarketID]['Name'])
            IDs.append(MarketID)
            stations.append(self.SiteNames[MarketID]['Name'])
        sortindices = sorted(range(len(stations)), key=stations.__getitem__)
        for idx in sortindices:
            self.listbox_IDs.append(IDs[idx])
            self.listbox_stations.append(stations[idx])
        self.listbox_items.set(self.listbox_stations)
        lbox_height = min(len(self.GoodsRequired),self.config_listboxHeight)
        self.gui_listbox.config(height=lbox_height)
        if lbox_height == self.config_listboxHeight:
            self.gui_scrollbar.grid(column=2,row=0,sticky=(tk.N,tk.S))
        else:
            self.gui_scrollbar.grid_remove()
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
            self.current = {}
            for idx in self.gui_listbox.curselection():
                MarketID = self.listbox_IDs[int(idx)]
                for resource in self.GoodsRequired[MarketID].keys():
                    if resource not in self.current:
                        self.current[resource] = self.GoodsRequired[MarketID][resource]
                    else:
                        self.current[resource] += self.GoodsRequired[MarketID][resource]
            goods=""
            values=""
            total = 0
            keys_sorted = list(self.current.keys())
            keys_sorted.sort()
            for resource in keys_sorted:
                goods += resource+":\n"
                values += str(self.current[resource])+"\n"
                total += self.current[resource]
            self.goods_string.set(goods[:-1])
            self.values_string.set(values[:-1])
            self.totals_string.set(str(total))

#---------- handle storage of data

    def startup_data_retrieval(self):
        main_thread_not_running = True
        # wait until the main thread has started the tkinter main loop
        while main_thread_not_running:
            try:
                self.gui_frame.event_generate("<<Dummy-Event>>")
                main_thread_not_running = False
            except:
                time.sleep(0.1)
        if self.do_file_storage:
            self.read_data()
        if (self.do_ftp_storage and self.ftp_server and
            self.ftp_user and self.ftp_password and self.ftp_filepath):
            time.sleep(0.5)
            self.do_ftp_get()

    def get_storage_string(self, local_storage = True):
        #start with a "StationNames" pseudo event
        #  store on the names of the sites we actually track
        namesdict = {"event":"StationNames" ,
                     "Station_IDs":self.listbox_IDs.copy(),
                     "StationNames":self.listbox_stations.copy()}
        if not local_storage:
            for marketID in self.DepotEvents.keys():
                if marketID not in namesdict["Station_IDs"]:
                     namesdict["Station_IDs"].append(marketID)
                     namesdict["StationNames"].append(self.SiteNames[marketID]['Name'])
        outstring = json.dumps(namesdict)+'\n'
        for marketID in self.DepotEvents.keys():
            timediff = datetime.now(dt.UTC) - self.DepotEventTimestamps[marketID]
            if ((marketID in self.listbox_IDs) and
                (timediff.total_seconds() < self.storage_timeout)):
                outstring += json.dumps(self.DepotEvents[marketID])+'\n'
            elif ((timediff.total_seconds() < self.storage_timeout) and
                  (self.DepotEvents[marketID]['ConstructionComplete'] or
                   self.DepotEvents[marketID]['ConstructionFailed'])):
                #untracked but finished sites get stored with long timeout
                #print('Storing finished site',marketID)
                outstring += json.dumps(self.DepotEvents[marketID])+'\n'
            elif ((not local_storage) and (timediff.total_seconds() < self.untracked_timeout)):
                #untracked and unfinished sites time out faster
                #print('Storing untracked site',marketID)
                outstring += json.dumps(self.DepotEvents[marketID])+'\n'
            else:
                #if not local_storage: print('Market',marketID,'timed out.')
                pass
        return outstring

    def data_to_file(self, filepath):
        #print("Writing data to:",filepath)
        with open(filepath, 'wt') as filehandle:
            filehandle.write(self.get_storage_string())
        return
        
    def save_data(self):
        if (self.worker_thread and self.worker_thread.is_alive()):
            #print("save_data: Worker Thread still busy.")
            return
        if self.worker_thread:
            self.worker_thread.join();
        if (self.do_file_storage and self.storage_file):
            self.worker_thread = threading.Thread(target=lambda:self.data_to_file(self.storage_file),
                                                  name="Worker")
            self.worker_thread.start()

    def read_data(self):
        if (self.do_file_storage and self.storage_file and
            os.path.isfile(self.storage_file)):
            with open(self.storage_file, 'rt') as filehandle:
                for line in filehandle:
                    entry = json.loads(line)
                    #print(entry['event'])
                    if (entry['event'] == 'StationNames'):
                        for index in range(len(entry['Station_IDs'])):
                            marketID = entry['Station_IDs'][index]
                            if marketID not in self.SiteNames:
                                system,station = entry['StationNames'][index].split(':')
                                self.SiteNames[marketID] = {}
                                self.SiteNames[marketID]['StationName'] = station
                                self.SiteNames[marketID]['System'] = system
                                self.SiteNames[marketID]['Name'] = entry['StationNames'][index]
                    if (entry['event'] == 'ColonisationConstructionDepot'):
                        self.worker_event.clear()
                        self.gui_frame.after(10, lambda: self.UpdateGoods(entry));
                        self.worker_event.wait() #wait for the main thread to be done with processing
                        time.sleep(0.1) # I like how this makes it look

    def do_ftp_store(self):
        #print('do_ftp_store called in:',threading.current_thread().name)
        #check if our ftp-data is recent
        if  not (self.ftp_server and self.ftp_user and
                 self.ftp_password and self.ftp_filepath):
            self.ftp_status = 'Error while storing file:\n Need server, username, password, AND filename!'
            self.gui_frame.after(10, self.update_ftp_status)
            return
        self.ftp_status = ""
        tdiff = datetime.now() - self.last_ftp_download
        if tdiff.total_seconds() > self.ftp_download_delay:
            #can do it from here as we are the worker!
            self.do_ftp_get()
            time.sleep(0.5)
        storage_string = self.get_storage_string(local_storage=False)
        file_obj = BytesIO(storage_string.encode('utf-8'))
        try:
            with ftplib.FTP(self.ftp_server) as ftp:
                ftp.login(user=self.ftp_user, passwd=self.ftp_password)
                ftp.storbinary(f"STOR {self.ftp_filepath}", file_obj)
        except ftplib.error_perm as excep :
            print('Failed to store file to server: '+repr(excep))
            self.ftp_status = 'Failed to store file to server:\n '+str(excep)
        except Exception as excep:
            print('Error while storing file: '+repr(excep))
            self.ftp_status = 'Error while storing file:\n '+str(excep)
        #print("file stored on ftp")
        self.last_ftp_upload = datetime.now()
        self.gui_frame.after(10, self.update_ftp_status)

    def ftp_store(self, num_retries = 0):
        if (self.worker_thread and self.worker_thread.is_alive()):
            if num_retries > self.ftp_upload_retries:
                print("ftp_store: Worker Thread still busy after",num_retries,"retries, aborting.")
                return
            else:
                #print("ftp_store: Worker Thread busy, now at",num_retries,"retries.")
                self.gui_frame.after(1000, lambda: self.ftp_store(num_retries+1))
                return
        #else:
        #    print("ftp_store: Worker Thread not busy after",num_retries,"retries.")
        if self.worker_thread:
            self.worker_thread.join();
        if (self.do_ftp_storage and self.ftp_server and
            self.ftp_user and self.ftp_password and self.ftp_filepath):
            # we have all required data and are asked to do it
            self.worker_thread = threading.Thread(target=self.do_ftp_store, name="Worker")
            self.worker_thread.start()

    def do_ftp_get(self):
        #print('do_ftp_get called in:',threading.current_thread().name)
        if  not (self.ftp_server and self.ftp_user and
                 self.ftp_password and self.ftp_filepath):
            self.ftp_status = 'Error while retrieving file:\n Need server, username, password, AND filename!'
            self.gui_frame.after(10, self.update_ftp_status)
            return
        self.ftp_status = ""        
        try:
            file_obj = BytesIO()
            with ftplib.FTP(self.ftp_server) as ftp:
                ftp.login(user=self.ftp_user, passwd=self.ftp_password)
                ftp.retrbinary(f"RETR {self.ftp_filepath}", file_obj.write)
            file_obj.seek(0)
            for line in file_obj:
                entry = json.loads(line)
                if (entry['event'] == 'StationNames'):
                    for index in range(len(entry['Station_IDs'])):
                        marketID = entry['Station_IDs'][index]
                        if marketID not in self.SiteNames:
                            system,station = entry['StationNames'][index].split(':')
                            self.SiteNames[marketID] = {}
                            self.SiteNames[marketID]['StationName'] = station
                            self.SiteNames[marketID]['System'] = system
                            self.SiteNames[marketID]['Name'] = entry['StationNames'][index]
                if (entry['event'] == 'ColonisationConstructionDepot'):
                    pseudoname = "MarketID "+str(entry['MarketID'])
                    self.worker_event.clear()
                    self.gui_frame.after(1, lambda: self.UpdateGoods(entry,System="Unknown System",
                                                                      StationName=pseudoname));
                    self.worker_event.wait() #wait for the main thread to be done with processing
                    time.sleep(0.1) #give the gui some time to avoid strange effects
        except ftplib.error_perm as excep :
            print('Failed to retrieve file from server: '+repr(excep))
            self.ftp_status = 'Failed to retrieve file from server:\n '+str(excep)
        except Exception as excep:
            print('Error while retrieving file: '+repr(excep))
            self.ftp_status = 'Error while retrieving file:\n '+str(excep)
        self.last_ftp_download = datetime.now()
        #print('file retrieved from ftp')
        self.gui_frame.after(10, self.update_ftp_status)

    def ftp_get(self):
        if (self.worker_thread and self.worker_thread.is_alive()):
            #print("Worker Thread still busy.")
            return
        if self.worker_thread:
            self.worker_thread.join();
        if (self.do_ftp_storage and self.ftp_server and
            self.ftp_user and self.ftp_password and self.ftp_filepath):
            # we have all required data and are asked to do it
            self.worker_thread = threading.Thread(target=self.do_ftp_get, name="Worker")
            self.worker_thread.start()

