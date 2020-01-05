# -*- coding: utf-8 -*-

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QStyle

from qgis.core import QgsApplication
import os

from geo2france.utils.plugin_globals import PluginGlobals
from geo2france.utils.singleton import Singleton


@Singleton
class PluginIcons():
    """
    """

    def __init__(self):
        """
        """

        # Folder icon
        QgsApplication.initQgis()
        style = QgsApplication.style()
        self.folder_icon = style.standardIcon(QStyle.SP_DirClosedIcon)

        warn_icon_path = os.path.join(PluginGlobals.instance().images_dir_path,
                                      PluginGlobals.instance().ICON_WARN_FILE_NAME)
        self.warn_icon = QIcon(warn_icon_path)

        wms_layer_icon_path = os.path.join(PluginGlobals.instance().images_dir_path,
                                           PluginGlobals.instance().ICON_WMS_LAYER_FILE_NAME)
        self.wms_layer_icon = QIcon(wms_layer_icon_path)

        wms_style_icon_path = os.path.join(PluginGlobals.instance().images_dir_path,
                                           PluginGlobals.instance().ICON_WMS_STYLE_FILE_NAME)
        self.wms_style_icon = QIcon(wms_style_icon_path)

        wfs_layer_icon_path = os.path.join(PluginGlobals.instance().images_dir_path,
                                           PluginGlobals.instance().ICON_WFS_LAYER_FILE_NAME)
        self.wfs_layer_icon = QIcon(wfs_layer_icon_path)

        raster_layer_icon_path = os.path.join(PluginGlobals.instance().images_dir_path,
                                              PluginGlobals.instance().ICON_RASTER_LAYER_FILE_NAME)
        self.raster_layer_icon = QIcon(raster_layer_icon_path)
