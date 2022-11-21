# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QTreeWidgetItem, QMenu
from qgis.PyQt.QtCore import Qt

from idg.toolbelt import PluginGlobals


def expand_item_and_subitems(item):
    """
    """
    if not item.isExpanded():
        item.setExpanded(True)
  
    nb_subitems = item.childCount()
  
    for i in range(nb_subitems):
        expand_item_and_subitems(item.child(i))


def collapse_item_and_subitems(item):
    """
    """
    if item.isExpanded():
        item.setExpanded(False)
  
    nb_subitems = item.childCount()
  
    for i in range(nb_subitems):
        collapse_item_and_subitems(item.child(i))


def contains_unexpanded_subitems(item):
    """
    """
    if not item.isExpanded():
        return True
  
    nb_subitems = item.childCount()
  
    for i in range(nb_subitems):
        if contains_unexpanded_subitems(item.child(i)):
            return True
  
    return False


class TreeWidgetItem(QTreeWidgetItem):
    """
    An item of the Géo2France tree view
    """
  
    def __init__(self, parent, item_data=None):
        """
        """
        QTreeWidgetItem.__init__(self, parent)
    
        # Item data
        self.item_data = item_data
    
        # Item title and description
        self.setText(0, item_data.title)
        self.setToolTip(0, item_data.description)
    
        # Item icon
        icon = self.item_data.icon
        if icon is not None:
            self.setIcon(0, icon)
        
        # QT flags
        # Enable selection and drag of the item
        if self.item_data.can_be_added_to_map:
            self.setFlags(Qt.ItemIsDragEnabled | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        else:
            self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    def run_default_action(self):
        """
        """
        if self.item_data.can_be_added_to_map:
            self.run_add_to_map_action()

    def run_add_to_map_action(self):
        """
        Add the resource to the map
        """
        self.item_data.run_add_to_map_action()

    def run_show_metadata_action(self):
        """
        Displays the resource metadata
        """
        self.item_data.run_show_metadata_action()

    def contains_unexpanded_subitems(self):
        """
        Determines if subitems are not expanded
        """
        if not self.isExpanded():
            return True
        else:
            return contains_unexpanded_subitems(self)

    def run_expand_all_subitems_action(self):
        """
        Expands all subitems
        """
        expand_item_and_subitems(self)

    def run_collapse_all_subitems_action(self):
        """
        Expands all subitems
        """
        collapse_item_and_subitems(self)

    def run_report_issue_action(self):
        """
        Report an issue
        """
        self.item_data.run_report_issue_action()

    def create_menu(self):
        """
        Creates a contextual menu
        """
        menu = QMenu()
    
        if self.item_data.can_be_added_to_map:
            add_to_map_action = menu.addAction(u"Ajouter à la carte")
            add_to_map_action.triggered.connect(self.run_add_to_map_action)
    
        if self.item_data.metadata_url:
            show_metadata_action = menu.addAction(u"Afficher les métadonnées...")
            show_metadata_action.triggered.connect(self.run_show_metadata_action)
    
        if self.childCount() > 0 and self.contains_unexpanded_subitems():
            expand_all_subitems_action = menu.addAction(u"Afficher tous les descendants")
            expand_all_subitems_action.triggered.connect(self.run_expand_all_subitems_action)
    
        if self.childCount() > 0 and self.isExpanded():
            expand_all_subitems_action = menu.addAction(u"Masquer tous les descendants")
            expand_all_subitems_action.triggered.connect(self.run_collapse_all_subitems_action)
    
        return menu

    def is_an_empty_group(self):
        """
        Indicates if this tem is an empty group
        """
        child_count = self.childCount()
    
        if child_count == 0:
            return self.item_data.node_type == PluginGlobals.instance().NODE_TYPE_FOLDER
        else:
            for i in range(child_count):
                if not self.child(i).is_an_empty_group():
                    return False
            return True
