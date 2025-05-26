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

    def prefs_ui(self, parent: nb.Notebook):
        frame = nb.Frame(parent)
        nb.Label(frame, text="Hello").grid()
        return frame

