# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QWidget, QDockWidget, QVBoxLayout

from geo2france.gui.tree_widget import TreeWidget


class DockWidget(QDockWidget):
    """
    The dock widget containing the tree view displaying the Géo2France resources
    """

    def __init__(self, parent = None):
        """
        """
        super(DockWidget, self).__init__()
        objectName = 'SimpleAccessDock'
        self.init_gui()

    def init_gui(self):
        """
        """
        self.setWindowTitle(u'Géo2France')
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.treeWidget = TreeWidget()

        self.layout = QVBoxLayout()
        self.layout.setSpacing(2)
        self.layout.setMargin(0)
        self.layout.addWidget(self.treeWidget)

        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setLayout(self.layout)
        self.setWidget(self.dockWidgetContents)

    def set_tree_content(self, resources_tree):
        """
        Creates the items of the tree widget
        """
        self.treeWidget.set_tree_content(resources_tree)
        self.update_visibility_of_tree_items()

    def update_visibility_of_tree_items(self):
        """
        Update the visibility of tree items:
        - visibility of empty groups
        - visibility of items with status = warn
        """
        self.treeWidget.update_visibility_of_tree_items()

    def dockStateChanged(self, floating):
        """
        """
        if floating:
            self.resize(300, 450)
        else:
            pass
