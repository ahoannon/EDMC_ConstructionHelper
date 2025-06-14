# EDMC_ConstructionHelper

A plugin for the [Elite: Dangerous Market Connector](https://github.com/EDCD/EDMarketConnector) (aka **EDMC**) to help you keep track of the goods required for
colonization construction projects.

## Installation

Download the `.zip` file and unpack it into the `plugins/` directory of **EDMC**, which is shown in the `Plugins` tab of the `Settings` window of **EDMC**

See also the relevant page on the [EDMC Wiki](https://github.com/EDCD/EDMarketConnector/wiki/Plugins)

## Usage
 
When **EDMC** is started with the ConstructionHelper running, then there will be a space on the main **EDMC** window with a listbox on top and a button 
to open or close the overlay window on the bottom. 

![Screenshot of empty EDMC main window](doc/EDMC_Main.png)

Once you docked at one or more active construction sites then the listbox will contain names of all known construction sites and the space between the 
listbox and the overlay window button will contain a list of all the goods that you need to finish the selected construction site(s).

### Multiple Construction Sites

Once you have docked at a construction site that you haven't visited previously and wasn't know to the plugin then a name for this site (the plugin will try to come 
up with something short and useful) is added to the listbox and the needed goods will be displayed by selecting that new entry in the listbox.

If you have visited more than one construction site then you can select multiple sites in the listbox. If you do so then the list of needed goods will be 
the sum of the goods needed for all selected sites.

If you select no site then the list of needed goods will be empty.\
If you visit a new construction site then the selection will be reset to only this new site as mentioned earlier.

### Overlay Window

The overlay button will open (or close) an overlay window that contains the same list of needed goods as the main window. It is a simple borderless window that
tries to stay above all other windows, in particular the **ED** game window. If it will be visible for you will depend on your setup. It does work for me on my 
Linux system and it seems to work on a typical windows system if **ED** is not running in fullscreen mode but e.g. in borderless mode. 
By default the overlay window will be in the top left corner of your (primary) screen but that can be changed.\
Note: if you can't see the overlay window, check if there is a list of goods displayed in the main **EDMC** window. If there isn't then the overlay window is a 
small, easy to miss, dark rectangle in the corner of your screen. (And it may be fully transparent, making it impossible to see.)

[<picture>
  <img src="https://raw.githubusercontent.com/ahoannon/EDMC_ConstructionHelper/refs/heads/main/doc/Overlay_Linux.png" 
   alt="Screenshot of the overlay window on my Linux where transparency doesn't work" height="200" />
</picture>](https://raw.githubusercontent.com/ahoannon/EDMC_ConstructionHelper/refs/heads/main/doc/Overlay_Linux.png)
[<picture>
  <img src="https://raw.githubusercontent.com/ahoannon/EDMC_ConstructionHelper/refs/heads/main/doc/Overlay_Windows.png" 
   alt="Screenshot of the overlay window on a Windows system with working transparency" height="200" />
</picture>](https://raw.githubusercontent.com/ahoannon/EDMC_ConstructionHelper/refs/heads/main/doc/Overlay_Windows.png)

### Customization

[<picture>
  <img src="https://raw.githubusercontent.com/ahoannon/EDMC_ConstructionHelper/refs/heads/main/doc/Preferences.png" 
   alt="Screenshot Preferences.png" height="200" />
</picture>](https://raw.githubusercontent.com/ahoannon/EDMC_ConstructionHelper/refs/heads/main/doc/Preferences.png)

You can set parameters for the overlay window in the preferences. No real range- or other checking is done. So if you enter invalid values then it will probably 
fail in some random way or another. The string for the colors can either be a hex RGB value like the default for the text color, or a color name that TK 
understands.

## Technical Stuff

This plugin is based on the `ColonisationConstructionDepot` logfile event that **FDev** introduced with the "Corsair" update on Tuesday April 8th 2025.
It identifies construction sites by the fact that it sees such an event from there and then tries to come up with a suitable name for the station with the same 
MarketID. 

## Licence 

This software is licensed under the [GNU General Public License v3.0](https://github.com/ahoannon/EDMC_ConstructionHelper/blob/main/LICENSE). 

Greetings, CMDR Hans Wijn

## ToDo 

- find and fix bugs
- display current ship cargo
- sort goods by category
- handle localized goods names
- option to use the [EDMC Overlay](https://github.com/inorton/EDMCOverlay) plugin instead of the TK window
