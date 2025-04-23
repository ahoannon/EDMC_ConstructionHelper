"""
Quick and really dirty ConstructionHelper plugin
(I man really, really dirty!)

Just dump a list of required resources onto the console
"""

from EDMC_ConstructionHelper import ConstructionHelper

ConstHelper = None

def plugin_start3(plugin_dir):
    global ConstHelper;
    ConstHelper = ConstructionHelper(plugin_dir);
    return 'ConstructionHelper';

def plugin_stop():
    global ConstHelper;
    ConstHelper = None
    return None;

def journal_entry(cmdr, is_beta, system, station, entry, state):
    global ConstHelper;
    if (entry['event'] == 'ColonisationConstructionDepot'):
        ConstHelper.UpdateGoods(entry,System=system,StationName=station);
    if ((entry['event'] == 'Location') or (entry['event'] == 'Docked')):
        ConstHelper.UpdateStations(entry);

        
def plugin_app(parent):
    global ConstHelper;
    return ConstHelper.init_gui(parent)
    
