from qgis.core import QgsDataItemProvider, QgsDataCollectionItem, QgsDataItem, QgsDataProvider, QgsProject, \
    QgsLayerTreeLayer, QgsLayerTreeGroup, QgsMimeDataUtils, QgsAbstractMetadataBase
from qgis.gui import QgisInterface
from qgis.PyQt.QtGui import QIcon
from idg.toolbelt import PluginGlobals, PlgOptionsManager, PluginIcons
from qgis.PyQt.QtWidgets import QAction, QMenu

import os.path
import json
import webbrowser


def find_catalog_url(metadata: QgsAbstractMetadataBase):
    """Find and return catalog url from layer metadatabase"""
    for l in metadata.links():
        if l.name.strip().lower() in ['metadata', 'métadonnées', 'métadonnée']:
            return l.url
    return None


class IdgProvider(QgsDataItemProvider):
    def __init__(self):
        QgsDataItemProvider.__init__(self)

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
        self.setIcon(QIcon(PluginGlobals.instance().plugin_path+'/resources/images/snowman-face-svgrepo-com.svg'))
        
    def actions(self, parent):
        actions = list()
        add_idg_action = QAction(QIcon(), 'Paramètres...', parent)
        
        actions.append(add_idg_action)
        return actions
        
    def menus(self, parent):
        menu = QMenu(title='Plateformes', parent=parent)
        for pf, checked in zip(['DataGrandEst', 'GeoBretagne', 'Geo2France', 'Indigeo'], [True, False, True, False]): # pour maquette TODO boucler sur une variable de conf
            action = QAction(pf, menu, checkable=True)
            action.setChecked(checked)
            menu.addAction(action) # TODO l'action permet d'activer/désactiver une plateforme. La désactivation supprime le DataCollectionItem et désactive le download du fichier de conf
        menu.addSeparator()
        menu.addAction(QAction('Ajouter une URL...', menu, )) # TODO Liens vers le panneau Options de QGIS
        return [menu]
        
    def createChildren(self):
        children = []
        for pf in json.loads(PlgOptionsManager().get_value_from_key(key='platforms')):
            pf_collection = PlatformCollection(name=pf['name'].lower(), label=pf['name'], url=pf['url'])
            children.append(pf_collection)
        return children


class PlatformCollection(QgsDataCollectionItem):
    def __init__(self, name, url, label=None, icon=None, parent=None):
        self.url = PluginGlobals.instance().config_file_path # TODO prevoir pour plusieurs fichier de conf
        self.path = "/IDG/"+name
        QgsDataCollectionItem.__init__(self, parent, label, self.path )
        self.setToolTip(self.url)
        self.project = QgsProject()
        self.project.read(self.url)
        if icon:  # QIcon
            self.setIcon(icon)

    def createChildren(self):
        # TODO add layer/folder for each platform
        children = []
        for element in self.project.layerTreeRoot().children():
            if isinstance(element, QgsLayerTreeLayer):
                children.append(LayerItem(parent=self, name=element.layer().name(), layer=element.layer()))
            elif isinstance(element, QgsLayerTreeGroup):
                children.append(GroupItem(parent=self, name=element.name(), group=element))
        return children


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

    def mimeUri(self):
        # Définir le mime est nécessaire pour le drag&drop
        return QgsMimeDataUtils.Uri(self.layer)

    def mimeUris(self):
        return [QgsMimeDataUtils.Uri(self.layer)]

    def hasDragEnabled(self):
        #TODO ajouter une couche via le drag fait perdre le style, car ouvre directement la couche sans passer par le projet
        return False

    def handleDoubleClick(self):
        QgsProject.instance().addMapLayer(self.layer)
        return True

    def hasChildren(self):
        return False

    def openUrl(self):
        webbrowser.open_new_tab(self.catalog_url)

    def actions(self, parent):
        ac_open_meta = QAction('Voir les métadonnées', parent)
        if self.catalog_url is not None:
            ac_open_meta.triggered.connect(self.openUrl)
        else:
            ac_open_meta.setEnabled(False)
        actions = [
            QAction('Afficher la couche', parent),
            ac_open_meta,
        ]
        return actions
