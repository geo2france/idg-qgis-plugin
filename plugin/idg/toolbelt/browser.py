from qgis.core import Qgis, QgsDataItemProvider, QgsDataCollectionItem, QgsDataItem, QgsDataProvider, QgsProject, \
    QgsLayerTreeLayer, QgsLayerTreeGroup, QgsMimeDataUtils, QgsAbstractMetadataBase, QgsApplication, QgsIconUtils
from qgis.gui import QgisInterface
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.Qt import QWidget
from idg.toolbelt import PluginGlobals, PlgOptionsManager
from .remote_platforms import RemotePlatforms
from idg.__about__ import __title__
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.utils import iface
import os.path
import webbrowser


def find_catalog_url(metadata: QgsAbstractMetadataBase):
    """Find and return catalog url from layer metadatabase"""
    for l in metadata.links():
        if l.name.strip().lower() in ['metadata', 'métadonnées', 'métadonnée']:
            return l.url
    return None

def project_custom_icon_url(metadata: QgsAbstractMetadataBase):
    for l in metadata.links():
        if l.name.lower().strip() == 'icon':
            return l.url
    return None


class IdgProvider(QgsDataItemProvider):
    def __init__(self, iface: QgisInterface):
        self.iface = iface
        QgsDataItemProvider.__init__(self)

    def name(self):
        return "IDG Provider"

    def capabilities(self):
        return QgsDataProvider.Net

    def createDataItem(self, path, parentItem):
        self.root = RootCollection(self.iface)
        return self.root
  
        
class RootCollection(QgsDataCollectionItem):
    def __init__(self, iface: QgisInterface):
        self.iface = iface
        QgsDataCollectionItem.__init__(self, None, "IDG", "/IDG")
        self.setIcon(QIcon(PluginGlobals.instance().plugin_path+'/resources/images/layers-svgrepo-com.svg'))
        self.setState(Qgis.BrowserItemState.Populating)

    def actions(self, parent):
        actions = list()
        add_idg_action = QAction(QIcon(), self.tr('Settings...'), parent)
        add_idg_action.triggered.connect(
            lambda: self.iface.showOptionsDialog(
                currentPage="mOptionsPage{}".format(__title__)
            )
        )
        actions.append(add_idg_action)
        return actions
        
    def menus(self, parent):
        menu = QMenu(title=self.tr('Plateforms'), parent=parent)
        menu.setEnabled(False)  # dev
        for pf, checked in zip(['DataGrandEst', 'GeoBretagne', 'Geo2France', 'Indigeo'], [True, False, True, False]): # pour maquette TODO boucler sur une variable de conf
            action = QAction(pf, menu, checkable=True)
            action.setChecked(checked)
            menu.addAction(action) # TODO l'action permet d'activer/désactiver une plateforme. La désactivation supprime le DataCollectionItem et désactive le download du fichier de conf
        menu.addSeparator()
        menu.addAction(QAction(self.tr('Add URL'), menu, )) # TODO Liens vers le panneau Options de QGIS
        return [menu]

    def repopulate(self):
        self.refresh()
        for pf in RemotePlatforms().plateforms :
            if pf.is_hidden() :
                continue
            pf_collection = PlatformCollection(plateform=pf)
            self.addChildItem(pf_collection, refresh=True)
        self.setState(Qgis.BrowserItemState.Populated)


class PlatformCollection(QgsDataCollectionItem):
    def __init__(self, plateform, parent=None):
        self.url = plateform.url
        self.path = "/IDG/"+plateform.idg_id.lower()
        QgsDataCollectionItem.__init__(self, parent, plateform.idg_id, self.path )
        self.setToolTip(plateform.abstract)
        self.project = plateform.project
        self.plateform = plateform
        self.setName(plateform.title)
        if self.project is None:
            self.setIcon(QIcon(QgsApplication.iconPath("mIconWarning.svg")))
        else:
            if plateform.icon is not None :  # Custom icon
                self.setIcon(plateform.icon)
            else :
                self.setIcon(QIcon(QgsApplication.iconPath("mIconFolderProject.svg")))  # Default Icon

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

        def hide_plateform(pf):
            pf.hide()
            iface.mainWindow().findChildren(QWidget, 'Browser')[0].refresh()

        actions = []
        for link in self.project.metadata().links():
            if link.name.lower() != 'icon':
                actions.append(set_action_url(link))
        separator = QAction(QIcon(), '', parent)
        separator.setSeparator(True)
        actions.append(separator)
        hide_action = QAction(self.tr('Hide'), parent )
        hide_action.triggered.connect(lambda: hide_plateform(self.plateform) )
        actions.append(hide_action)
        return actions


class GroupItem(QgsDataCollectionItem):
    def __init__(self, parent, name, group):
        self.path = os.path.join(parent.path, group.name())
        self.group = group
        QgsDataCollectionItem.__init__(self, parent, name, self.path)
        self.setIcon(QIcon(QgsApplication.iconPath("mIconFolder.svg")))

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
        self.setIcon(QgsIconUtils.iconForLayer(self.layer))

    def mimeUri(self):
        # Définir le mime est nécessaire pour le drag&drop
        return QgsMimeDataUtils.Uri(self.layer)

    def mimeUris(self):
        return [QgsMimeDataUtils.Uri(self.layer)]

    def hasDragEnabled(self):
        #TODO ajouter une couche via le drag fait perdre le style, car ouvre directement la couche sans passer par le projet
        return False

    def handleDoubleClick(self):
        self.addLayer()
        return True

    def hasChildren(self):
        return False

    def openUrl(self):
        webbrowser.open_new_tab(self.catalog_url)

    def addLayer(self):
        self.layer.setDataSource(self.layer.source(), self.layer.name(),
                            self.layer.providerType())  # Reset datasource, à cause du flag FlagDontResolveLayers
        QgsProject.instance().addMapLayer(self.layer)

    def actions(self, parent):
        ac_open_meta = QAction(self.tr('Show metadata'), parent)
        if self.catalog_url is not None:
            ac_open_meta.triggered.connect(self.openUrl)
        else:
            ac_open_meta.setEnabled(False)

        ac_show_layer = QAction(self.tr('Display layer'), parent)
        ac_show_layer.triggered.connect(self.addLayer)
        
        actions = [
            ac_show_layer,
            ac_open_meta,
        ]
        return actions
