from qgis.core import QgsDataItemProvider, QgsDataCollectionItem, QgsDataItem, QgsDataProvider, QgsProject, \
    QgsLayerTreeLayer, QgsLayerTreeGroup, QgsMimeDataUtils, QgsAbstractMetadataBase, QgsApplication, QgsIconUtils
from qgis.PyQt.QtGui import QIcon

from idg.toolbelt.tree_node_factory import download_default_idg_list, download_all_config_files
from idg.toolbelt import PlgOptionsManager, PluginGlobals

import json
import os.path

class RemotePlatforms:
    def __init__(self):
        self.plateforms=[]
        with open(os.path.join(PluginGlobals.instance().config_dir_path,'default_idg.json')) as f : #Télécharger si non existant ?
            self.stock_idgs = json.load(f)
        self.custom_idg = PlgOptionsManager().get_plg_settings().custom_idgs.split(',')
        self.custom_idg.remove('')
        for k,v in self.stock_idgs.items():
            self.plateforms.append(Plateform(url=v, idg_id=k))

    def url_all(self):
        return self.url_stock() + self.url_custom()

    def url_custom(self):
        return self.custom_idg

    def url_stock(self):
        out = []
        for k,v in self.stock_idgs.items():
            if k not in PlgOptionsManager().get_plg_settings().hidden_idgs.split(','):
                out.append(v)
        print(out)
        return out


    def reset(self):
        rep = PluginGlobals.instance().config_dir_path
        for fichier in os.listdir(rep):
            chemin_fichier = os.path.join(rep, fichier)
            if fichier != 'default_idg.json':
                if os.path.isfile(chemin_fichier):
                    os.remove(chemin_fichier)

        download_default_idg_list()
        download_all_config_files(RemotePlatforms().stock_idgs)
        #TODO remove all local files (projects & images)


class Plateform:
    def __init__(self, url, idg_id):
        self.url=url
        self.idg_id=idg_id
        self.project=self.read_project()

    def read_project(self):
        p = QgsProject()
        if p.read(self.qgis_project_filepath(),QgsProject.ReadFlags() | QgsProject.FlagDontResolveLayers | QgsProject.FlagDontLoadLayouts) is not True : # Le flag permet d'éviter que les URL des layers soient interrogées, mais le datasource du layer doit être reset avant usage
            return None
        return p
    def qgis_project_filepath(self):
        suffix = os.path.splitext(os.path.basename(self.url))[-1]  # .qgs ou .qgz
        local_file_name = os.path.join(PluginGlobals.instance().config_dir_path, self.idg_id + suffix)
        return local_file_name
    def is_custom(self):
        # Comparer avec les pf stock
        pass

    def is_hidden(self):
        if self.idg_id in PlgOptionsManager().get_plg_settings().hidden_idgs.split(','):
            return True
        return False

    def title(self):
        pass

    def icon(self):
        for l in self.project.metadata().links():
            if l.name.lower().strip() == 'icon':
                icon_suffix = os.path.splitext(os.path.basename(l.url))[-1]
                return QIcon(os.path.join(PluginGlobals.instance().config_dir_path, str(self.idg_id) + icon_suffix))
        return None

    def download(self):
        pass