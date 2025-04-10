"""
EDMC Construction Helper class
"""

class ConstructionHelper():
    def __init__(self, plugin_dir):

        self.SiteNames = {}
        self.GoodsRequired = {}

    def UpdateStations(self,entry):
        if (('MarketID' in entry) and
            (entry['MarketID'] not in self.SiteNames)):
            if 'StationName_Localised' in entry:
                StationName = entry['StationName_Localised']
            else:
                StationName = entry['StationName']
            self.SiteNames[entry['MarketID']] = [StationName,entry['StarSystem']]
        
        
    def UpdateGoods(self,entry):
        if (entry['ConstructionComplete'] == False and
            entry['ConstructionFailed'] == False
            ):
            current = {}
            for resource in entry['ResourcesRequired']:
                amount = resource['RequiredAmount'] - resource['ProvidedAmount']
                if (amount>0):
                    current[resource['Name_Localised']] = amount;
            if not current:
                print("\nMarket no complete or failed but no goods required for ID:",entry['MarketID'])
                return False
            if (entry['MarketID'] not in self.GoodsRequired or
                self.GoodsRequired[entry['MarketID']] != current ):
                # Goods required new or updated
                self.GoodsRequired[entry['MarketID']] = current
                if entry['MarketID'] not in self.SiteNames:
                    print("\n MarketID",entry['MarketID'],"not in list of table names")
                    return
                print("\nConstruction resources required for Market:",self.SiteNames[entry['MarketID']])
                for resource in current:
                    print(resource,':',current[resource]);

