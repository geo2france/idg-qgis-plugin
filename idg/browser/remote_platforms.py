import json
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from qgis.core import QgsProject, Qgis
from qgis.PyQt.QtGui import QIcon

from idg.toolbelt import PlgOptionsManager, PlgLogger

from idg.plugin_globals import PluginGlobals

log = PlgLogger().log


class RemotePlatforms:
    def __init__(self, read_projects=True):
        self.plateforms = []

        try:
            with open(PluginGlobals.REMOTE_DIR_PATH / PluginGlobals.DEFAULT_CONFIG_FILE_NAME) as f: # Ouvrir le fichier dans remote s'il existe et > à 0 octets
                self.stock_idgs = json.load(f)
        except  (json.JSONDecodeError, FileNotFoundError ): # Fichier remote non trouvé
            with open(PluginGlobals.CONFIG_FILE_PATH) as f:
                self.stock_idgs = json.load(f)

        self.custom_idgs = PlgOptionsManager().get_plg_settings().custom_idgs
        for e in self.stock_idgs:
            try :
                self.plateforms.append(
                    Plateform(url=e['url'], idg_id=e['name'], read_project=read_projects)
                )
            except TypeError:
                log('Error reading default_idj.json, please reload all remote files', log_level=Qgis.Warning, push=False)
                # Probably use old style default_idg.json structure

    def get_url_all(self):
        """Get the URLs of all stock platforms and non-hidden custom platforms)."""
        return self.get_url_stock() + self.get_url_custom()

    def get_url_custom(self):
        """Get all the custom platforms URLs."""
        return self.custom_idgs

    def get_url_stock(self):
        """Get the URLs of the non-hidden custom platforms."""
        stock_urls = []
        for k, v in self.stock_idgs.items():
            if k not in PlgOptionsManager().get_plg_settings().hidden_idgs:
                stock_urls.append(v)
        return stock_urls


class Plateform:
    def __init__(self, url, idg_id, read_project=True):
        self.url = url
        self.idg_id = idg_id
        self.project = None
        if read_project:
            self.read_project()

    def read_project(self):
        p = QgsProject()
        if (
            p.read(
                str(self.qgis_project_filepath()),
                QgsProject.ReadFlags()
                | QgsProject.FlagDontResolveLayers
                | QgsProject.FlagDontLoadLayouts,
            )
            is not True
        ):  # Le flag permet d'éviter que les URL des layers soient interrogées, mais le datasource du layer doit être reset avant usage
            return None
        self.project = p
        return p

    def qgis_project_filepath(self):
        project_file_name = Path(urlparse(self.url).path).name
        local_file_path = PluginGlobals.REMOTE_DIR_PATH / self.idg_id / project_file_name
        return local_file_path

    def is_custom(self):
        # Comparer avec les pf stock
        pass

    def is_hidden(self):
        if self.idg_id in PlgOptionsManager().get_plg_settings().hidden_idgs:
            return True
        return False

    @property
    def title(self):
        return self.project.metadata().title() or self.idg_id

    @property
    def abstract(self):
        return self.project.metadata().abstract()

    def hide(self):
        settings = PlgOptionsManager().get_plg_settings()

        hidden_igs = settings.hidden_idgs
        if self.idg_id not in hidden_igs:
            hidden_igs.append(self.idg_id)
        settings.hidden_idgs = hidden_igs

        PlgOptionsManager().save_from_object(settings)

    @property
    def icon(self) -> Optional[QIcon]:
        if self.icon_url is not None :
            icon_file_name = Path(urlparse(self.icon_url).path).name
            return QIcon(str(PluginGlobals.REMOTE_DIR_PATH / self.idg_id / icon_file_name))
        return None

    @property
    def icon_url(self) -> Optional[str]:
        try :
            for link in self.project.metadata().links():
                if link.name.lower().strip() == "icon":
                    return link.url
            return None
        except AttributeError:
            return None

    def download(self):
        pass
