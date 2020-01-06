# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QTreeWidget, QAbstractItemView
from qgis.PyQt.QtCore import Qt, QByteArray, QDataStream, QIODevice
from qgis.core import Qgis, QgsMessageLog

from geo2france.gui.tree_items import TreeWidgetItem
from geo2france.utils.plugin_globals import PluginGlobals


class TreeWidget(QTreeWidget):
    """
    The tree widget used in the Géo2France dock
    """

    def __init__(self):
        objectName = 'TreeWidget'

        super(TreeWidget, self).__init__()

        # Selection
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        # Columns and headers
        self.setColumnCount(1)
        self.setHeaderLabel('')
        self.setHeaderHidden(True)

        # Events
        self.itemDoubleClicked.connect(self.tree_item_double_clicked)

        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)

        # Enable drag of tree items
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

    def set_tree_content(self, resources_tree):
        """
        Creates the items of the tree widget
        """

        def create_subitem(subtree, parent_item=self):
            """
            """
            subitem = TreeWidgetItem(parent_item, subtree)
            if subtree.children is not None and len(subtree.children) > 0:
                for child in subtree.children:
                    create_subitem(child, subitem)

        self.clear()

        if resources_tree is None:
            QgsMessageLog.logMessage(u"Faute de fichier de configuration valide, aucune ressource ne peut être chargée "
                                     u"dans le panneau de l'extension Géo2France.",
                                     tag=u"Géo2France", level=Qgis.Warning)
        elif resources_tree.children is not None and len(resources_tree.children) > 0:
            for child in resources_tree.children:
                create_subitem(child, self)

    def update_visibility_of_tree_items(self):
        """
        Update the visibility of tree items:
        - visibility of empty groups
        - visibility of items with status = warn
        """
        hide_items_with_warn_status = PluginGlobals.instance().HIDE_RESOURCES_WITH_WARN_STATUS
        hide_empty_groups = PluginGlobals.instance().HIDE_EMPTY_GROUPS

        def update_visibility_of_subitems(item, hide_empty_groups, hide_items_with_warn_status):

            if hasattr(item, "item_data") and item.item_data.status == PluginGlobals.instance().NODE_STATUS_WARN:
                item.setHidden(hide_items_with_warn_status)

            child_count = item.childCount()
            if child_count > 0:
                for i in range(child_count):
                    sub_item = item.child(i)
                    if sub_item.is_an_empty_group():
                        sub_item.setHidden(hide_empty_groups)

                    update_visibility_of_subitems(sub_item, hide_empty_groups, hide_items_with_warn_status)

        update_visibility_of_subitems(self.invisibleRootItem(), hide_empty_groups, hide_items_with_warn_status)

    def tree_item_double_clicked(self, item, column):
        """
        Handles double clic on an item
        """
        item.run_default_action()

    def open_menu(self, position):
        """
        Handles context menu in the tree
        """
        selected_item = self.currentItem()
        menu = selected_item.create_menu()
        menu.exec_(self.viewport().mapToGlobal(position))

    # Constant and methods used for drag and drop of tree items onto the map

    QGIS_URI_MIME = "application/x-vnd.qgis.qgis.uri"

    def mimeTypes(self):
        """
        """
        return [self.QGIS_URI_MIME]

    def mimeData(self, items):
        """
        """
        mime_data = QTreeWidget.mimeData(self, items)
        encoded_data = QByteArray()
        stream = QDataStream(encoded_data, QIODevice.WriteOnly)

        for item in items:
            layer_mime_data = item.item_data.layer_mime_data()
            stream.writeQString(layer_mime_data)

        mime_data.setData(self.QGIS_URI_MIME, encoded_data)
        return mime_data

    def dropMimeData(self, parent, index, data, action):
        """
        """
        if action == Qt.IgnoreAction:
            return True

        return False
