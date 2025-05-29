"""
Quick and really dirty ConstructionHelper plugin
(I man really, really dirty!)

Just dump a list of required resources onto the console
"""

from EDMC_ConstructionHelper import ConstructionHelper
from ConstHelper_Preference import CH_Preferences

ConstHelper = None
PrefsUI = None

def plugin_start3(plugin_dir):
    global ConstHelper;
    ConstHelper = ConstructionHelper(plugin_dir);
    return ConstHelper.Prefix

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
        ConstHelper.initiate_ftp_get(entry);
    if (entry['event'] == 'ColonisationContribution'):
        ConstHelper.initiate_ftp_send()
       
def plugin_app(parent):
    global ConstHelper;
    return ConstHelper.init_gui(parent)
    

def plugin_prefs(parent, cmdr, is_beta):
    global PrefsUI;
    PrefsUI = CH_Preferences(ConstHelper.Prefix)
    return PrefsUI.prefs_ui(parent);

def prefs_changed(cmdr, is_beta):
    global ConstHelper;
    global PrefsUI;
    PrefsUI.save_preferences()
    ConstHelper.get_config()
    ConstHelper.safe_data()
    ConstHelper.fix_theme()
