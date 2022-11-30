from qgis.core import QgsDataItemProvider, QgsDataCollectionItem, QgsDataProvider
from qgis.PyQt.QtGui import QIcon
from idg.toolbelt import PluginGlobals 


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
            
    def createChildren(self):
        return []
