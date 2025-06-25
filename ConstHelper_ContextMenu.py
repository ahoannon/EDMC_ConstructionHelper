"""
Class that implements context menus for the Construction Helper
"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mbox
import time

class ContextMenus:
    def __init__(self, frame, listbox, construction_helper):
        """Create and set up the context menu for the listbox"""
        self.parent = frame
        self.listbox = listbox
        self.const_helper = construction_helper
        self.listbox_menu = tk.Menu(self.listbox, tearoff=tk.FALSE)
        self.listbox_menu.add_command(label="Remove Selected Site(s) from List", accelerator="<double-click>",
                                      command=self.remove_site)
        self.listbox_menu.add_command(label="Copy Selected System(s) to Clipboard", accelerator= "<Ctrl+Shift+C>",
                                      command=self.copy_system_to_clipboard)
        self.listbox_menu.add_command(label="Mark this Site as Completed", command=self.site_completed)
        self.listbox_menu.add_command(label="Copy Goods to Clipboard (as Table)", command=self.export_goods_to_spreadsheet)        
        # Bind right-click event to listbox
        self.listbox.bind("<Button-3>", self.show_listbox_menu)  # Right-click on Windows/Linux
        # make the context menus go away when it looses the mouse focus
        self.listbox.bind("<FocusOut>", self.hide_context_menu)
        
        self.labels_menu = tk.Menu(self.parent, tearoff=tk.FALSE)
        self.labels_menu.add_command(label="Copy Selected System(s) to Clipboard", accelerator= "<Ctrl+Shift+C>",
                                      command=self.copy_system_to_clipboard)
        self.labels_menu.add_command(label="Copy Goods to Clipboard (as Table)", command=self.export_goods_to_spreadsheet)
        self.labels_menu.add_command(label="Retrieve FTP data now", command=self.retrieve_ftp_data)
        self.labels_menu.add_command(label="Store data to FTP now", command=self.send_ftp_data)
        
        # Bind right-click event to parent
        self.parent.bind("<Button-3>", self.show_labels_menu)  # Right-click on Windows/Linux

    def add_labels_binding(self, widget):
        widget.bind("<Button-3>", self.show_labels_menu)            

    def show_listbox_menu(self, event):
        """Show context menu at cursor position"""
        if self.labels_menu:
            self.labels_menu.unpost()
        #set focus on listbox so that "<FocusOut>" works
        self.listbox.focus_set()
        # Select the item under cursor
        index = self.listbox.nearest(event.y)
        if index < self.listbox.size():
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)
            self.listbox.activate(index)
            self.const_helper.update_values()
        # Show context menu
        try:
            #self.listbox_menu.tk_popup(event.x_root, event.y_root)            
            self.listbox_menu.post(event.x_root, event.y_root)
        finally:
            self.listbox_menu.grab_release()

    def show_labels_menu(self, event):
        if self.listbox_menu:
            self.listbox_menu.unpost()
        #set focus on listbox so that "<FocusOut>" works
        self.listbox.focus_set()
        if self.const_helper.do_ftp_storage:
            self.labels_menu.entryconfigure("Retrieve FTP data now", state=tk.NORMAL)
            self.labels_menu.entryconfigure("Store data to FTP now", state=tk.NORMAL)
        else:
            self.labels_menu.entryconfigure("Retrieve FTP data now", state=tk.DISABLED)
            self.labels_menu.entryconfigure("Store data to FTP now", state=tk.DISABLED)
        # Show labels context menu
        try:
            self.labels_menu.post(event.x_root, event.y_root)
        finally:
            self.labels_menu.grab_release()
            
    def hide_context_menu(self, event=None):
        #print("hide_context_menu called")
        if self.listbox_menu:
            self.listbox_menu.unpost()
        if self.labels_menu:
            self.labels_menu.unpost()

    def remove_site(self):
        #print("remove_site called")
        self.const_helper.remove_sites()

    def site_completed(self):
        self.const_helper.mark_site_completed()

    def copy_system_to_clipboard(self):
        #print("copy_system_to_clipboard called")
        self.const_helper.clip_system_names()

    def export_goods_to_spreadsheet(self):
        #print("export_goods_to_spreadsheet called")
        self.const_helper.clip_resources_spreadsheet()

    def retrieve_ftp_data(self):
        self.const_helper.ftp_confirm_transfer = True
        self.const_helper.initiate_ftp_get()

    def send_ftp_data(self):
        self.const_helper.ftp_confirm_transfer = True
        self.const_helper.initiate_ftp_send()

        
