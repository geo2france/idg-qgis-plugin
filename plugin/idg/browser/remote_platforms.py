import json
import os.path

from qgis.core import QgsProject
from qgis.PyQt.QtGui import QIcon

from idg.toolbelt import PlgOptionsManager
from idg.plugin_globals import PluginGlobals


class RemotePlatforms:
    def __init__(self, read_projects=True):
        self.plateforms = []
        with open(PluginGlobals.instance().config_file_path) as f:
            self.stock_idgs = json.load(f)
        self.custom_idg = PlgOptionsManager().get_plg_settings().custom_idgs.split(",")
        self.custom_idg.remove("")
        for k, v in self.stock_idgs.items():
            self.plateforms.append(
                Plateform(url=v, idg_id=k, read_project=read_projects)
            )

    def url_all(self):
        return self.url_stock() + self.url_custom()

    def url_custom(self):
        return self.custom_idg

    def url_stock(self):
        out = []
        for k, v in self.stock_idgs.items():
            if k not in PlgOptionsManager().get_plg_settings().hidden_idgs.split(","):
                out.append(v)
        print(out)
        return out


class Plateform:
    def __init__(self, url, idg_id, read_project=True):
        self.url = url
        self.idg_id = idg_id
        if read_project:
            self.project = self.read_project()

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
        return p

    def qgis_project_filepath(self):
        suffix = os.path.splitext(os.path.basename(self.url))[-1]  # .qgs ou .qgz
        local_file_name = self.idg_id + suffix
        local_file_path = PluginGlobals.instance().config_dir_path / local_file_name
        return local_file_path

    def is_custom(self):
        # Comparer avec les pf stock
        pass

    def is_hidden(self):
        if self.idg_id in PlgOptionsManager().get_plg_settings().hidden_idgs.split(","):
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
        hidden_pf = settings.hidden_idgs.split(",")
        if self.idg_id not in hidden_pf:
            hidden_pf.append(self.idg_id)
        settings.hidden_idgs = ",".join(hidden_pf)
        PlgOptionsManager().save_from_object(settings)

    @property
    def icon(self):
        for link in self.project.metadata().links():
            if link.name.lower().strip() == "icon":
                icon_suffix = os.path.splitext(os.path.basename(link.url))[-1]
                icon_file_name = str(self.idg_id) + icon_suffix
                return QIcon(
                    str(PluginGlobals.instance().config_dir_path / icon_file_name)
                )
        return None

    def download(self):
        pass
