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
        nb.Label(frame, text=label_text).grid(row=row, column=column*2, sticky=tk.E)
        value = config.get_str(self.Prefix+key)
        entry = nb.EntryMenu(frame)
        entry.insert(0, value)
        entry.grid(row=row, column=(column*2)+1, sticky=tk.EW)
        setattr(self, f"{key}_entry", entry)

    def prefs_ui(self, parent: nb.Notebook):
        frame = nb.Frame(parent)
        nb.Label(frame, text="Settings for the overlay window. "
                 "Close and re-open the overlay for setting to take effect.").grid(row=0, column=0, columnspan=4)
        self.create_label_entry(frame, "X-Position (pixels to the right of top left corner):", "overlayX", 0, 1 )
        self.create_label_entry(frame, "Y-Position (pixels down from top left corner):", "overlayY", 0, 2 )
        self.create_label_entry(frame, "Font Size:", "fontSize", 0, 3 )
        self.create_label_entry(frame, "Foreground Color:", "overlayFG", 0, 4)
        self.create_label_entry(frame, "Background Color:", "overlayBG", 0, 5)
        self.create_label_entry(frame, "Transparency (1-100):", "Alpha", 0, 6)

        return frame


    def save_preferences(self):
        config.set(self.Prefix+"overlayX", int(self.overlayX_entry.get()))
        config.set(self.Prefix+"overlayY", int(self.overlayY_entry.get()))
        config.set(self.Prefix+"fontSize", int(self.fontSize_entry.get()))
        config.set(self.Prefix+"overlayFG", self.overlayFG_entry.get())
        config.set(self.Prefix+"overlayBG", self.overlayBG_entry.get())
        config.set(self.Prefix+"Alpha", int(self.Alpha_entry.get()))
        
