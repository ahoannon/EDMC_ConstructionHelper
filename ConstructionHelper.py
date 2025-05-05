#!/usr/bin/env python3
"""
Standalone version of the EDMC_ConstructionHelper

"""

import tkinter as tk
import logging
import os
import json
from EDMC_ConstructionHelper import ConstructionHelper


journal_directory = '/home/driss/Elite-Dangerous-Journals'

# setup logger in case I'll actually use it sometime
#logger = logging.getLogger(__name__)
#logging.basicConfig(filename='ConstructionHelper.log', level=logging.INFO)
logging.getLogger().addHandler(logging.NullHandler())

#global variables
current_System = 'Unknown System'
current_Station = 'Unknown Station'
ConstHelper = None
journal_path = ''
file = None

def find_journal(directory):
    oldtime = ''
    newfile = ''
    try:
        files = os.listdir(directory)
        for file in files:
            parts = file.split(sep='.')
            if parts[0] == 'Journal' and len(parts) == 4:
                #use string comparison to compare times
                #this works as long as the format doesn't change
                if parts[1] > oldtime:
                    oldtime=parts[1]
                    newfile = file
        if not newfile:
            gui_statvar.set('No journal file found in:\n'+directory)
    except FileNotFoundError:
        gui_statvar.set('Not a valid path:\n'+directory)
    return os.path.join(directory,newfile)

def send_events_from_file(filehandle):
    for line in filehandle:
        entry = json.loads(line)
        if (entry['event'] == 'ColonisationConstructionDepot'):
            ConstHelper.UpdateGoods(entry,System=current_System,StationName=current_Station);
        if ((entry['event'] == 'Location') or (entry['event'] == 'Docked')):
            ConstHelper.UpdateStations(entry);

def send_events():
    global file
    global journal_path
    if file:
        send_events_from_file(file)
    newjournal = find_journal(gui_dirvar.get())
    if (os.path.isfile(newjournal) and
        newjournal != journal_path):
        journal_path = newjournal
        gui_statvar.set('Reading from Journal file:\n'+newjournal)
        if file:
            file.close()
        file = open(journal_path,'r')
        if file:
            send_events_from_file(file)
    # call me again in 100 milliseconds
    root.after(200,send_events)


root = tk.Tk()
root.title("Construction Helper")
gui_L1 = tk.Label(root,text="Path to journal files:")
gui_dirvar = tk.StringVar()
gui_dirvar.set(journal_directory)
gui_E1 = tk.Entry(root,textvariable=gui_dirvar,width=30)
gui_statvar = tk.StringVar()
gui_statvar.set("Just Started")
gui_L2 = tk.Label(root,textvariable=gui_statvar,justify=tk.LEFT)
gui_sep = tk.ttk.Separator(root,orient=tk.HORIZONTAL)
root.grid_columnconfigure(0, weight=1)
gui_L1.grid(row=0,sticky=tk.W)
gui_E1.grid(row=1,sticky=(tk.W,tk.E))
gui_L2.grid(row=2,sticky=tk.W)
gui_sep.grid(row=3,sticky=(tk.W,tk.E))

myfile = find_journal(gui_dirvar.get())

#start the Construction Helper gui
ConstHelper = ConstructionHelper(os.getcwd());
gui_CH_frame = ConstHelper.init_gui(root)
gui_CH_frame.grid(row=4,sticky=(tk.W,tk.E,tk.N,tk.S))

# start polling function
root.after(100,send_events)

root.mainloop()
