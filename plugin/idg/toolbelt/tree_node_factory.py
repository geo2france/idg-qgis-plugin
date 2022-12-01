# -*- coding: utf-8 -*-

import os
import json
import traceback
from urllib.parse import parse_qs, urlparse

from qgis.core import (
    Qgis,
    QgsMessageLog,
    QgsProject,
    QgsNetworkAccessManager,
    QgsNetworkReplyContent,
)
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.PyQt.QtCore import QUrl

from idg.toolbelt import PluginGlobals
from .nodes import WmsLayerTreeNode, WmsStyleLayerTreeNode, WmtsLayerTreeNode, WfsFeatureTypeTreeNode
from .nodes import WfsFeatureTypeFilterTreeNode, GdalWmsConfigFileTreeNode, FolderTreeNode


def download_tree_config_file(file_url):
    """
    Download the resources tree file
    """
    try:
        # replace content of local config file by content of online config file
        with open(PluginGlobals.instance().config_file_path, "w") as local_config_file:

            request = QNetworkRequest(QUrl(file_url))
            manager = QgsNetworkAccessManager.instance()
            response: QgsNetworkReplyContent = manager.blockingGet(
                request, forceRefresh=True
            )

            if response.error() != QNetworkReply.NoError:
                raise Exception(f"{response.error()} - {response.errorString()}")

            data_raw_string = bytes(response.content()).decode("utf-8")
            data = json.loads(data_raw_string)

            json.dump(data, local_config_file, ensure_ascii=False, indent=2)

    except Exception as e:
        short_message = "Le téléchargement du fichier de configuration du plugin {0} a échoué.".format(
            PluginGlobals.instance().PLUGIN_TAG
        )
        PluginGlobals.instance().iface.messageBar().pushMessage(
            "Erreur", short_message, level=Qgis.Critical
        )

        long_message = "{0}\nUrl du fichier : {1}\n{2}\n{3}".format(
            short_message, file_url, e.__doc__, e
        )
        QgsMessageLog.logMessage(
            long_message, tag=PluginGlobals.instance().PLUGIN_TAG, level=Qgis.Critical
        )


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
            raise #dev

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
            node = self.auto_node_type(node_title, node_type, node_description,
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

    def auto_node_type(self, node_title, node_type, node_description,
                                        node_status, node_metadata_url, node_params, parent_node):
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
        return node
    def build_tree_from_project_file(self, project):
        node = FolderTreeNode(title='Project title')
        for element in project.layerTreeRoot().children():
            if hasattr(element,'layer'):
                layer = element.layer()
                params=self.extract_params_from_layer(layer) # Sortir de l'URL les paramètres nécessaire (url, version, name, srs)
                node_type=self.provider_to_node_type(layer.dataProvider().name())
                node.children.append(self.auto_node_type(node_title=layer.name(), node_type=node_type, node_description=layer.metadata().abstract(),
                                              node_status=None, node_metadata_url=next(iter(layer.metadata().links()),''), node_params=params, parent_node=node))
        return node

    def extract_params_from_layer(self, layer):
        out=dict()
        out['srs'] = layer.crs().authid()
        if layer.dataProvider().name().lower() == 'wms':
            parsed_url = urlparse('http://0.0.0.0?' + layer.source()) #Ajout d'un host fictif pour parser l'url car la source wms n'en contient pas
            out['url'] = layer.source() #certains parametre sont doublés (layers, srs, etc..) mais pas gênant
            out['name'] = parse_qs(parsed_url.query)['layers'][0]
            out['format'] = parse_qs(parsed_url.query)['format'][0]
            out['version'] = layer.dataProvider().htmlMetadata().split('<tr><td>WMS Version</td><td>')[1][:5]
            return out
        elif layer.dataProvider().name().lower() == 'wfs':
            parsed_url = urlparse(layer.source())
            out['url'] = layer.source()
            out['name'] = parse_qs(parsed_url.query)['TYPENAME'][0]
            out['version'] = parse_qs(parsed_url.query)['VERSION'][0]
            return out

    def provider_to_node_type(self, provider_key):
        """
        Convert qgis provider key to node_type
        """
        mapping = {'wfs':'wfs_feature_type', 'wms':'wms_layer','wmts': 'wmts_layer'}
        return mapping[provider_key.lower()]