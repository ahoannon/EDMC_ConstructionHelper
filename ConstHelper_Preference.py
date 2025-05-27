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
        
    def prefs_ui(self, parent: nb.Notebook):
        frame = nb.Frame(parent)
        nb.Label(frame, text="Settings for the overlay window. "
                 "Close and re-open the overlay for settings to take effect.").grid(row=0, column=0, columnspan=4)
        self.create_label_entry(frame, "X-Position (pixels to the right of top left corner):", "overlayX", 0, 1 )
        self.create_label_entry(frame, "Y-Position (pixels down from top left corner):", "overlayY", 0, 2 )
        self.create_label_entry(frame, "Font Size (character height in pixels, 0=default):", "fontSize", 0, 3 )
        self.create_label_entry(frame, "Text Color (TK color string):", "overlayFG", 0, 4)
        self.create_label_entry(frame, "Background Color (TK color string):", "overlayBG", 0, 5)
        self.create_label_entry(frame, "Transparency (1 invisible - 100 opaque):", "Alpha", 0, 6)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=7, columnspan=4, padx=2, pady=2, sticky=tk.EW)
        self.DoFile_var = tk.IntVar()
        self.file_storage_button = nb.Checkbutton(frame, text="Store construction data to file", variable=self.DoFile_var,
                                                  command=self.toggle_file_entry)
        self.file_storage_button.grid(row=8, column=0,columnspan=4)
        self.create_label_entry(frame, "Storage file incl. path:", "storage_file", 0, 9)
        self.storage_file_entry.grid(columnspan=3)
        self.DoFile_var.set(config.get_bool(self.Prefix+"DoFile"))
        self.toggle_file_entry()
        return frame


    def save_preferences(self):
        config.set(self.Prefix+"overlayX", str(int(self.overlayX_entry.get())))
        config.set(self.Prefix+"overlayY", str(int(self.overlayY_entry.get())))
        config.set(self.Prefix+"fontSize", str(int(self.fontSize_entry.get())))
        config.set(self.Prefix+"overlayFG", self.overlayFG_entry.get())
        config.set(self.Prefix+"overlayBG", self.overlayBG_entry.get())
        config.set(self.Prefix+"Alpha", str(int(self.Alpha_entry.get())))
        config.set(self.Prefix+"storage_file", self.storage_file_entry.get())
        config.set(self.Prefix+"DoFile", bool(self.DoFile_var.get()))
