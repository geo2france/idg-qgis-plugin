# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QAction, QMenu
# TODO
# from builtins import object
# from qgis.PyQt.QtGui import QIcon
# from qgis.core import QgsApplication

import os.path

from geo2france.utils.plugin_globals import PluginGlobals
# TODO
# from geo2france.gui.dock import DockWidget
from geo2france.gui.about_box import AboutBox
from geo2france.gui.param_box import ParamBox
from geo2france.nodes.treenodefactory import TreeNodeFactory
from geo2france.nodes.treenodefactory import download_tree_config_file


class SimpleAccessPlugin:
    """
    Plugin initialisation.
    A json config file is read in order to configure the plugin GUI.
    """

    def __init__(self, iface):
        self.iface = iface
        self.dock = None

        PluginGlobals.instance().set_plugin_path(os.path.dirname(os.path.abspath(__file__)))
        PluginGlobals.instance().set_plugin_iface(self.iface)
        PluginGlobals.instance().reload_globals_from_qgis_settings()

        config_struct = None
        config_string = ""

        # Download the config if needed
        if self.need_download_tree_config_file():
            download_tree_config_file(PluginGlobals.instance().CONFIG_FILE_URLS[0])

        # Read the resources tree file and update the GUI
        self.ressources_tree = TreeNodeFactory(PluginGlobals.instance().config_file_path).root_node

# TODO
    def need_download_tree_config_file(self):
        """
        Do we need to download a new version of the resources tree file?
        2 possible reasons:
        - the user wants it to be downloading at plugin start up
        - the file is currently missing
        """

        return (PluginGlobals.instance().CONFIG_FILES_DOWNLOAD_AT_STARTUP > 0 or
                not os.path.isfile(PluginGlobals.instance().config_file_path))

    def initGui(self):
        """
        Plugin GUI initialisation.
        Creates a menu item in the menu of QGIS
        Creates a DockWidget containing the tree of resources
        """

        # Create a menu
        self.createPluginMenu()

# TODO
        # Create a dockable panel with a tree of resources
        # self.dock = GpicDockWidget()
        # self.dock.setTreeContents(self.ressources_tree)
        # self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)

    def createPluginMenu(self):
        """
        Creates the plugin main menu
        """

        plugin_menu = self.iface.pluginMenu()
        self.plugin_menu = QMenu(u"Géo2France", plugin_menu)
        plugin_menu.addMenu(self.plugin_menu)

        show_panel_action = QAction(u'Afficher le panneau latéral', self.iface.mainWindow())
        show_panel_action.triggered.connect(self.showPanelMenuTriggered)
        self.plugin_menu.addAction(show_panel_action)

        param_action = QAction(u'Paramétrer le plugin…', self.iface.mainWindow())
        param_action.triggered.connect(self.paramMenuTriggered)
        self.plugin_menu.addAction(param_action)

        about_action = QAction(u'À propos…', self.iface.mainWindow())
        about_action.triggered.connect(self.aboutMenuTriggered)
        self.plugin_menu.addAction(about_action)

    def showPanelMenuTriggered(self):
        """
        Shows the dock widget
        """
        self.dock.show()
        pass

    def aboutMenuTriggered(self):
        """
        Shows the About box
        """

        dialog = AboutBox(self.iface.mainWindow())
        dialog.exec_()

    def paramMenuTriggered(self):
        """
        Shows the Param box
        """
        dialog = ParamBox(self.iface.mainWindow(), self.dock)
        dialog.exec_()

    def unload(self):
        """
        Removes the plugin menu
        """
        self.iface.pluginMenu().removeAction(self.plugin_menu.menuAction())

# TODO
    # def showTasDialog(self):
    #     """
    #     Affiche la boîte de dialogue de création des tableaux d'assemblage
    #     :return:       None
    #     """
    #     if self.tas_dialog is None:
    #         self.tas_dialog = tas_dlg.TasDlg(self.iface)
    #
    #     self.tas_dialog.setVisible(not self.tas_dialog.isVisible())
    #
    #     # if self.main_dialog.isVisible():
    #     #     self.layer_manager.reset_layers()
    #
    # def showTacGeoPdfF5Dialog(self):
    #     """
    #     Affiche la boîte de dialogue de création des tableaux de coupures GeoPdf F5
    #     :return:       None
    #     """
    #     if self.tac_geopdf_f5_dialog is None:
    #         self.tac_geopdf_f5_dialog = tcp_geopdf_f5_dlg.TcpGeoPdfF5Dlg(self.iface)
    #
    #     self.tac_geopdf_f5_dialog.setVisible(not self.tac_geopdf_f5_dialog.isVisible())
    #
    #     # if self.main_dialog.isVisible():
    #     #     self.layer_manager.reset_layers()
    #
    # def openTasDialogTriggered(self):
    #     """
    #     Evènement activé quand l'utilisateur clique sur la barre d'outil ou sur le menu
    #     :return:       None
    #     """
    #     self.showTasDialog()
    #
    # def openTacDialogTriggered(self):
    #     """
    #     Evènement activé quand l'utilisateur clique sur la barre d'outil ou sur le menu
    #     :return:       None
    #     """
    #     self.showTacGeoPdfF5Dialog()
