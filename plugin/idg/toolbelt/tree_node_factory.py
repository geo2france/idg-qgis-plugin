# -*- coding: utf-8 -*-

import os
import json
import traceback
from urllib.parse import parse_qs, urlsplit, urlencode
from urllib.request import Request, urlopen

from qgis.core import Qgis, QgsMessageLog, QgsProject

from idg.toolbelt import PluginGlobals
from .nodes import WmsLayerTreeNode, WmsStyleLayerTreeNode, WmtsLayerTreeNode, WfsFeatureTypeTreeNode
from .nodes import WfsFeatureTypeFilterTreeNode, GdalWmsConfigFileTreeNode, FolderTreeNode


def download_tree_config_file(file_url):
    """
    Download the resources tree file
    """
    try:
        # QgsMessageLog.logMessage("Config file URL: {}".format(file_url,
        #                                                       tag=PluginGlobals.instance().PLUGIN_TAG,
        #                                                       level=Qgis.Info))
        # Download the config file
        PluginGlobals.instance().iface.messageBar().pushMessage("Info", file_url)
        http_req = Request(file_url)
        http_req.add_header("Cache-Control", "no-cache")

        with urlopen(http_req) as response, open(PluginGlobals.instance().config_file_path, 'wb') as local_config_file:
            data = response.read()
            local_config_file.write(data)

    except Exception as e:
        short_message = u"Le téléchargement du fichier de configuration du plugin {0} a échoué.".format(
            PluginGlobals.instance().PLUGIN_TAG)
        PluginGlobals.instance().iface.messageBar().pushMessage("Erreur", short_message, level=Qgis.Critical)

        long_message = u"{0}\nUrl du fichier : {1}\n{2}\n{3}".format(short_message, file_url, e.__doc__, e)
        QgsMessageLog.logMessage(long_message, tag=PluginGlobals.instance().PLUGIN_TAG, level=Qgis.Critical)


class TreeNodeFactory:
    """
    Class used to build FavoritesTreeNode instances
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.root_node = None

        if not os.path.isfile(self.file_path):
            message = u"Le fichier de configuration du plugin {0} n'a pas pu être trouvé.".format(
                PluginGlobals.instance().PLUGIN_TAG)
            PluginGlobals.instance().iface.messageBar().pushMessage("Erreur", message, level=Qgis.Critical)
            QgsMessageLog.logMessage(message, tag=PluginGlobals.instance().PLUGIN_TAG, level=Qgis.Critical)
            return

        try:
        # Read the config file
        # QgsMessageLog.logMessage("Config file path: {}".format(self.file_path,
        #                                                        tag=PluginGlobals.instance().PLUGIN_TAG,
        #                                                        level=Qgis.Info))
            if PluginGlobals.instance().CONFIG_FILE_URLS[0].endswith('json'): # TODO parser proprement l'url
                with open(self.file_path, encoding='utf-8', errors='replace') as f:
                    config_string = "".join(f.readlines())
                    config_struct = json.loads(config_string)
                    self.root_node = self.build_tree(config_struct)
            else : # assume qgs/qgz file
                project = QgsProject()
                project.read(self.file_path)
                self.root_node = self.build_tree_from_project_file(project)

        except Exception as e:
            short_message = u"La lecture du fichier de configuration du plugin {0} a produit des erreurs.".format(
                PluginGlobals.instance().PLUGIN_TAG)
            PluginGlobals.instance().iface.messageBar().pushMessage("Erreur", short_message, level=Qgis.Critical)

            long_message = u"{0}\n{1}\n{2}".format(short_message, e.__doc__, e)
            QgsMessageLog.logMessage(long_message, tag=PluginGlobals.instance().PLUGIN_TAG, level=Qgis.Critical)
            QgsMessageLog.logMessage(
                "".join(traceback.format_exc()), tag=PluginGlobals.instance().PLUGIN_TAG, level=Qgis.Critical
            )
            QgsMessageLog.logMessage(
                "".join(traceback.format_stack()), tag=PluginGlobals.instance().PLUGIN_TAG, level=Qgis.Critical
            )
            raise Exception #dev

    def build_tree(self, tree_config, parent_node=None):
        """
        Function that do the job
        """

        # Read the node attributes
        node_title = tree_config.get('title', None)
        node_description = tree_config.get('description', None)
        node_type = tree_config.get('type', None)
        node_status = tree_config.get('status', None)
        node_metadata_url = tree_config.get('metadata_url', None)
        node_params = tree_config.get('params', None)

        if node_title:
            # Creation of the node
            if node_type == PluginGlobals.instance().NODE_TYPE_WMS_LAYER:
                node = WmsLayerTreeNode(node_title, node_type, node_description,
                                        node_status, node_metadata_url, node_params, parent_node)

            elif node_type == PluginGlobals.instance().NODE_TYPE_WMS_LAYER_STYLE:
                node = WmsStyleLayerTreeNode(node_title, node_type, node_description,
                                             node_status, node_metadata_url, node_params, parent_node)

            elif node_type == PluginGlobals.instance().NODE_TYPE_WMTS_LAYER:
                node = WmtsLayerTreeNode(node_title, node_type, node_description,
                                         node_status, node_metadata_url, node_params, parent_node)

            elif node_type == PluginGlobals.instance().NODE_TYPE_WFS_FEATURE_TYPE:
                node = WfsFeatureTypeTreeNode(node_title, node_type, node_description,
                                              node_status, node_metadata_url, node_params, parent_node)

            elif node_type == PluginGlobals.instance().NODE_TYPE_WFS_FEATURE_TYPE_FILTER:
                node = WfsFeatureTypeFilterTreeNode(node_title, node_type, node_description,
                                                    node_status, node_metadata_url, node_params, parent_node)

            elif node_type == PluginGlobals.instance().NODE_TYPE_GDAL_WMS_CONFIG_FILE:
                node = GdalWmsConfigFileTreeNode(node_title, node_type, node_description,
                                                 node_status, node_metadata_url, node_params, parent_node)

            else:
                node = FolderTreeNode(node_title, node_type, node_description,
                                      node_status, node_metadata_url, node_params, parent_node)

            # Creation of the node children
            node_children = tree_config.get('children', [])
            if len(node_children) > 0:
                for child_config in node_children:
                    child_node = self.build_tree(child_config, node)
                    node.children.append(child_node)

            return node

        else:
            return None

    def build_tree_from_project_file(self, project):
        node = FolderTreeNode(title='Project title')
        for element in project.layerTreeRoot().children():
            if hasattr(element,'layer'):
                layer = element.layer()
                params=dict(url=layer.source()) # Sortir de l'URL les paramètres nécessaire (url, version, name, srs)
                node.children.append(WfsFeatureTypeTreeNode(title=layer.name(), node_type='wfs_feature_type', description=layer.metadata().abstract(),
                                              status=None, metadata_url=next(iter(layer.metadata().links()),''), params=params, parent_node=node))
        return node

    def extract_params_from_url(self, url):
        p = parse_qs(urlsplit(url).query)
        base_url = list(parse_qs(url).keys())[0]
        other_parmas = p.copy()
        for k in ['TYPENAME','SRSNAME','VERSION']:
            other_parmas.pop(k, None)
        return dict(
            name=p.get('TYPENAME'),
            srs=p.get('SRSNAME'),
            version=p.get('VERSION'),
            url=base_url+urlencode(other_parmas)
        )