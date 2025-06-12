"""
Class that implements context menus for the Construction Helper
"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mbox
import time

class ListboxContextMenu:
    def __init__(self, listbox, construction_helper):
        """Create and set up the context menu for the listbox"""
        self.parent = listbox
        self.const_helper = construction_helper
        self.context_menu = tk.Menu(self.parent, tearoff=tk.FALSE)
        self.context_menu.add_command(label="Remove Site(s)", accelerator="<double-click>",
                                      command=self.remove_site)
        self.context_menu.add_command(label="Copy System(s) to Clipboard", accelerator= "<Ctrl+Shift+C>",
                                      command=self.copy_system_to_clipboard)
        self.context_menu.add_command(label="Export Goods for Spreadsheet", command=self.export_goods_to_spreadsheet)
        
        # Bind right-click event to listbox
        self.parent.bind("<Button-3>", self.show_context_menu)  # Right-click on Windows/Linux
        # make the context menu go away when it looses the mouse focus
        self.parent.bind("<FocusOut>", self.hide_context_menu)
    
    def show_context_menu(self, event):
        """Show context menu at cursor position"""
        #set focus on listbox so that "<FocusOut>" works
        self.parent.focus_set()
        # Select the item under cursor
        index = self.parent.nearest(event.y)
        if index < self.parent.size():
            self.parent.selection_clear(0, tk.END)
            self.parent.selection_set(index)
            self.parent.activate(index)
            self.const_helper.update_values()
        # Show context menu
        try:
            #self.context_menu.tk_popup(event.x_root, event.y_root)            
            self.context_menu.post(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
            
    def hide_context_menu(self, event=None):
        #print("hide_context_menu called")
        if self.context_menu:
            self.context_menu.unpost()

    def remove_site(self):
        #print("remove_site called")
        self.const_helper.remove_sites()

    def copy_system_to_clipboard(self):
        #print("copy_system_to_clipboard called")
        self.const_helper.clip_system_names()

    def export_goods_to_spreadsheet(self):
        print("export_goods_to_spreadsheet called")
        pass
