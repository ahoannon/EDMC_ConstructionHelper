"""
Handle the preferences for the EDMC_ConstructionHelper
"""
import tkinter as tk
from tkinter import ttk
import logging
import os

# ---- import EDMC classes ----
import myNotebook as nb
from config import appname, config
    
plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f'{appname}.{plugin_name}')
# The logger should have been set up by the EDMC core
if not logger.hasHandlers():
    print("I thought this wouldn't happen again in current version of EDMC!")
# ---- end EDMC classes ----

class CH_Preferences():
    def __init__(self, prefix):
        # the "Name" of this plugin that is used to differentiate it
        # from other plugins
        # This all will fail horribly if not set properly!
        self.Prefix = prefix;
        
    def create_label_entry(self, frame, label_text, key, column, row):
        label = nb.Label(frame, text=label_text)
        label.grid(row=row, column=column*2, sticky=tk.E)
        value = config.get_str(self.Prefix+key)
        entry = nb.EntryMenu(frame)
        entry.insert(0, value)
        entry.grid(row=row, column=(column*2)+1, sticky=tk.EW)
        setattr(self, f"{key}_entry", entry)
        setattr(self, f"{key}_label", label)

    def toggle_file_entry(self):
        if self.DoFile_var.get():
            self.storage_file_entry.config(state='normal')
            self.storage_file_label.config(state='normal')
        else:
            self.storage_file_entry.config(state='disabled')
            self.storage_file_label.config(state='disabled')
            
    def toggle_ftp_entry(self):
        if self.DoFTP_var.get():
            self.FTPlabel.config(state='normal')
            self.FTPServer_entry.config(state='normal')
            self.FTPServer_label.config(state='normal')
            self.FTPUser_entry.config(state='normal')
            self.FTPUser_label.config(state='normal')
            self.FTPPasswd_entry.config(state='normal')
            self.FTPPasswd_label.config(state='normal')
            self.FTPFilePath_entry.config(state='normal')
            self.FTPFilePath_label.config(state='normal')
        else:
            self.FTPlabel.config(state='disabled')
            self.FTPServer_entry.config(state='disabled')
            self.FTPServer_label.config(state='disabled')
            self.FTPUser_entry.config(state='disabled')
            self.FTPUser_label.config(state='disabled')
            self.FTPPasswd_entry.config(state='disabled')
            self.FTPPasswd_label.config(state='disabled')
            self.FTPFilePath_entry.config(state='disabled')
            self.FTPFilePath_label.config(state='disabled')
        
    def prefs_ui(self, parent: nb.Notebook):
        frame = nb.Frame(parent)
        frame.grid(sticky=tk.EW)
        frame_overlay = nb.Frame(frame)
        frame_overlay.grid(row=0, column=0)
        nb.Label(frame_overlay, text="Settings for the overlay window. "
                 "Close and re-open the overlay for settings to take effect.").grid(row=0, column=0, columnspan=4)
        self.create_label_entry(frame_overlay, "X-Position (pixels to the right of top left corner):", "overlayX", 0, 1 )
        self.create_label_entry(frame_overlay, "Y-Position (pixels down from top left corner):", "overlayY", 0, 2 )
        self.create_label_entry(frame_overlay, "Font Size (character height in pixels, 0=default):", "fontSize", 0, 3 )
        self.create_label_entry(frame_overlay, "Text Color (TK color string):", "overlayFG", 0, 4)
        self.create_label_entry(frame_overlay, "Background Color (TK color string):", "overlayBG", 0, 5)
        self.create_label_entry(frame_overlay, "Transparency (1 invisible - 100 opaque):", "Alpha", 0, 6)
        # general stuff
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=1, columnspan=4, padx=2, pady=(15,5), sticky=tk.EW)
        self.ShowEcon_var = tk.IntVar()
        self.show_economy__button = nb.Checkbutton(frame, text="Show economy composition of last station",
                                                  variable=self.ShowEcon_var)
        self.show_economy__button.grid(row=2, column=0, sticky=tk.W)
        self.ShowEcon_var.set(config.get_bool(self.Prefix+"ShowEconomy"))
        # Start of file storage stuff
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=3, columnspan=4, padx=2, pady=(15,5), sticky=tk.EW)
        frame_file = nb.Frame(frame)
        frame_file.grid(row=4, column=0)
        self.DoFile_var = tk.IntVar()
        self.file_storage_button = nb.Checkbutton(frame_file, text="Store construction data to file", variable=self.DoFile_var,
                                                  command=self.toggle_file_entry)
        self.file_storage_button.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.create_label_entry(frame_file, "Storage file incl. path:", "storage_file", 0, 1)
        self.storage_file_entry.config(width=60)
        self.DoFile_var.set(config.get_bool(self.Prefix+"DoFile"))
        self.toggle_file_entry()
        # start of ftp storage stuff
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=5, columnspan=4, padx=2, pady=(15,5), sticky=tk.EW)
        frame_ftp = nb.Frame(frame)
        frame_ftp.grid(row=6, column=0, sticky=tk.EW)
        self.DoFTP_var = tk.IntVar()
        self.ftp_storage_button = nb.Checkbutton(frame_ftp, text="Store data on a remote ftp server", variable=self.DoFTP_var,
                                                  command=self.toggle_ftp_entry)
        self.ftp_storage_button.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.FTPlabel = nb.Label(frame_ftp, text="  This is independent of file storage. "
                                 "May crash if remote ftp-data is corrupted.")
        self.FTPlabel.grid(row=1, column=0, columnspan=4, sticky=tk.W)
        self.create_label_entry(frame_ftp, "FTP server:", "FTPServer", 0, 2)
        self.FTPServer_entry.config(width=40)
        self.FTPServer_entry.grid(columnspan=3)
        self.create_label_entry(frame_ftp, "username:", "FTPUser", 0, 3)
        self.create_label_entry(frame_ftp, "password:", "FTPPasswd", 1, 3)
        self.create_label_entry(frame_ftp, "Path to file on Server:", "FTPFilePath", 0, 4)
        self.FTPFilePath_entry.grid(columnspan=3)
        self.DoFTP_var.set(config.get_bool(self.Prefix+"DoFTP"))
        self.toggle_ftp_entry()
        
        return frame


    def save_preferences(self):
        config.set(self.Prefix+"overlayX", str(int(self.overlayX_entry.get())))
        config.set(self.Prefix+"overlayY", str(int(self.overlayY_entry.get())))
        config.set(self.Prefix+"fontSize", str(int(self.fontSize_entry.get())))
        config.set(self.Prefix+"overlayFG", self.overlayFG_entry.get())
        config.set(self.Prefix+"overlayBG", self.overlayBG_entry.get())
        config.set(self.Prefix+"Alpha", str(int(self.Alpha_entry.get())))
        config.set(self.Prefix+"ShowEconomy", bool(self.ShowEcon_var.get()))
        config.set(self.Prefix+"DoFile", bool(self.DoFile_var.get()))
        config.set(self.Prefix+"storage_file", self.storage_file_entry.get())
        config.set(self.Prefix+"DoFTP", bool(self.DoFTP_var.get()))
        config.set(self.Prefix+"FTPServer", self.FTPServer_entry.get())
        config.set(self.Prefix+"FTPUser", self.FTPUser_entry.get())
        config.set(self.Prefix+"FTPPasswd", self.FTPPasswd_entry.get())
        config.set(self.Prefix+"FTPFilePath", self.FTPFilePath_entry.get())
        
