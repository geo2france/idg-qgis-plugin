from idg.toolbelt.tree_node_factory import download_default_idg_list
from idg.toolbelt import PlgOptionsManager, PluginGlobals

import json
import os.path

class RemotePlatforms:
    def __init__(self):
        with open(os.path.join(PluginGlobals.instance().config_dir_path,'default_idg.json')) as f : #Télécharger si non existant ?
            self.stock_idgs = json.load(f)
        self.custom_idg = PlgOptionsManager().get_plg_settings().custom_idgs.split(',')
        pass

    def url_all(self):
        return self.url_stock() + self.url_custom()

    def url_custom(self):
        return self.custom_idg

    def url_stock(self):
        return list(self.stock_idgs.values())

    def reset(self):
        pass
        #TODO remove all local files (projects & images)