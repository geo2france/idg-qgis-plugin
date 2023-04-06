from qgis.core import QgsDataItemProvider, QgsDataCollectionItem, QgsDataItem, QgsDataProvider, QgsProject, \
    QgsLayerTreeLayer, QgsLayerTreeGroup, QgsMimeDataUtils, QgsAbstractMetadataBase
from qgis.gui import QgisInterface
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication

from idg.toolbelt import PluginGlobals, PlgOptionsManager, PluginIcons, PlgTranslator
from qgis.PyQt.QtWidgets import QAction, QMenu

import os.path
import json
import webbrowser

# translation
plg_translation_mngr = PlgTranslator()
translator = plg_translation_mngr.get_translator()
if translator:
    QCoreApplication.installTranslator(translator)

def find_catalog_url(metadata: QgsAbstractMetadataBase):
    """Find and return catalog url from layer metadatabase"""
    for l in metadata.links():
        if l.name.strip().lower() in ['metadata', 'métadonnées', 'métadonnée']:
            return l.url
    return None


class IdgProvider(QgsDataItemProvider):
    def __init__(self):
        QgsDataItemProvider.__init__(self)
        self.tr = plg_translation_mngr.tr

    def name(self):
        return "IDG Provider"

    def capabilities(self):
        return QgsDataProvider.Net

    def createDataItem(self, path, parentItem):
        root = RootCollection()
        return root
  
        
class RootCollection(QgsDataCollectionItem):
    def __init__(self):
        QgsDataCollectionItem.__init__(self, None, "IDG", "/IDG")
        self.setIcon(QIcon(PluginGlobals.instance().plugin_path+'/resources/images/World-in-Hand-Big.svg'))
        self.tr = plg_translation_mngr.tr

    def actions(self, parent):
        actions = list()
        add_idg_action = QAction(QIcon(), self.tr('Settings...'), parent)
        
        actions.append(add_idg_action)
        return actions
        
    def menus(self, parent):
        menu = QMenu(title=self.tr('Plateforms'), parent=parent)
        for pf, checked in zip(['DataGrandEst', 'GeoBretagne', 'Geo2France', 'Indigeo'], [True, False, True, False]): # pour maquette TODO boucler sur une variable de conf
            action = QAction(pf, menu, checkable=True)
            action.setChecked(checked)
            menu.addAction(action) # TODO l'action permet d'activer/désactiver une plateforme. La désactivation supprime le DataCollectionItem et désactive le download du fichier de conf
        menu.addSeparator()
        menu.addAction(QAction(self.tr('Add URL'), menu, )) # TODO Liens vers le panneau Options de QGIS
        return [menu]
        
    def createChildren(self):
        children = []
        for idg_id, url in enumerate(PlgOptionsManager().get_value_from_key('idgs').split(',')):
            idg_id = str(idg_id)
            suffix = os.path.splitext(os.path.basename(url))[-1]
            local_file_name = os.path.join(PluginGlobals.instance().config_dir_path, idg_id + suffix)
            pf_collection = PlatformCollection(name=idg_id.lower(), label=idg_id, url=local_file_name)
            children.append(pf_collection)
        return children


class PlatformCollection(QgsDataCollectionItem):
    def __init__(self, name, url, label=None, icon=None, parent=None):
        self.url = url # TODO prevoir pour plusieurs fichier de conf
        self.path = "/IDG/"+name
        QgsDataCollectionItem.__init__(self, parent, label, self.path )
        self.setToolTip(self.url)
        self.project = QgsProject()
        if self.project.read(self.url, QgsProject.ReadFlags()|QgsProject.FlagDontResolveLayers|QgsProject.FlagDontLoadLayouts) \
                is not True:  # Le flag permet d'éviter que les URL des layers soient interrogées, mais le datasource du layer doit être reset avant usage
            print('error')
            self.setIcon(PluginIcons.instance().warn_icon)
        if (self.project.metadata().title() or '') != '':
            self.setName(self.project.metadata().title())
        if icon:  # QIcon
            self.setIcon(icon)

        self.tr = plg_translation_mngr.tr

    def createChildren(self):
        # TODO add layer/folder for each platform
        children = []
        for element in self.project.layerTreeRoot().children():
            if isinstance(element, QgsLayerTreeLayer):
                children.append(LayerItem(parent=self, name=element.layer().name(), layer=element.layer()))
            elif isinstance(element, QgsLayerTreeGroup):
                children.append(GroupItem(parent=self, name=element.name(), group=element))
        return children


    def actions(self, parent):
        #parent.setToolTipsVisible(True)
        def set_action_url(link):
            a = QAction(link.name, parent)
            a.triggered.connect(lambda: webbrowser.open_new_tab(link.url))
            #a.setToolTip(link.description)
            return a

        actions = []
        for link in self.project.metadata().links():
            actions.append(set_action_url(link))
        return actions


class GroupItem(QgsDataCollectionItem):
    def __init__(self, parent, name, group):
        self.path = os.path.join(parent.path, group.name())
        self.group = group
        QgsDataCollectionItem.__init__(self, parent, name, self.path)
        self.setIcon(PluginIcons.instance().folder_icon)

    def createChildren(self):
        children = []
        for element in self.group.children():
            if isinstance(element, QgsLayerTreeLayer):
                children.append(LayerItem(parent=self, name=element.layer().name(), layer=element.layer()))
            elif isinstance(element, QgsLayerTreeGroup):
                children.append(GroupItem(parent=self, name=element.name(), group=element))
        return children


class LayerItem(QgsDataItem):
    def __init__(self, parent, name, layer):
        self.layer = layer
        self.catalog_url = find_catalog_url(layer.metadata())
        self.path = os.path.join(parent.path, layer.id())
        QgsDataItem.__init__(self, QgsDataItem.Custom,
                             parent, name, self.path )
        self.setState(QgsDataItem.Populated)  # no children
        self.setToolTip(self.layer.metadata().abstract())
        self.tr = plg_translation_mngr.tr

    def mimeUri(self):
        # Définir le mime est nécessaire pour le drag&drop
        return QgsMimeDataUtils.Uri(self.layer)

    def mimeUris(self):
        return [QgsMimeDataUtils.Uri(self.layer)]

    def hasDragEnabled(self):
        #TODO ajouter une couche via le drag fait perdre le style, car ouvre directement la couche sans passer par le projet
        return False

    def handleDoubleClick(self):
        self.layer.setDataSource(self.layer.source(), self.layer.name(),
                            self.layer.providerType())  # Reset datasource, à cause du flag FlagDontResolveLayers
        QgsProject.instance().addMapLayer(self.layer)
        return True

    def hasChildren(self):
        return False

    def openUrl(self):
        webbrowser.open_new_tab(self.catalog_url)

    def actions(self, parent):
        ac_open_meta = QAction(self.tr('Show metadata'), parent)
        if self.catalog_url is not None:
            ac_open_meta.triggered.connect(self.openUrl)
        else:
            ac_open_meta.setEnabled(False)
        actions = [
            QAction(self.tr('Display layer'), parent),
            ac_open_meta,
        ]
        return actions
