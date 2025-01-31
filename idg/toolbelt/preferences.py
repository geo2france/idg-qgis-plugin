#! python3  # noqa: E265

"""
Plugin settings.
"""

# standard
from dataclasses import asdict, dataclass, fields, field, MISSING
from typing import List

# PyQGIS
from qgis.core import QgsSettings
from qgis.PyQt.QtCore import QVariant

# package
import idg.toolbelt
from idg.__about__ import __title__, __version__
from idg.plugin_globals import PluginGlobals

# ############################################################################
# ########## Classes ###############
# ##################################


@dataclass
class PlgSettingsStructure:
    """Plugin settings structure and defaults values."""

    # global
    debug_mode: bool = False
    version: str = __version__
    configs_folder: str = ""
    download_files_at_startup: bool = True
    custom_idgs: List[str] = field(default_factory=lambda: [])
    hidden_idgs: List[str] = field(default_factory=lambda: ["Géoplateforme"])
    config_file_url: str = (
        "https://raw.githubusercontent.com/geo2france/idg-qgis-plugin/"
        "dev/idg/config/default_idg.json"
    )


class PlgOptionsManager:
    @staticmethod
    def get_plg_settings() -> PlgSettingsStructure:
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings
        :rtype: PlgSettingsStructure
        """
        # get dataclass fields definition
        settings_fields = fields(PlgSettingsStructure())

        # retrieve settings from QGIS/Qt
        settings = QgsSettings()
        settings.beginGroup(__title__)

        # map settings values to preferences object
        settings_values = {}
        for i in settings_fields:
            value = None

            try:
                default_value = (
                    i.default_factory() if i.default is MISSING else i.default
                )
                value = settings.value(
                    key=i.name, defaultValue=default_value, type=i.type
                )
            except TypeError:
                value = settings.value(key=i.name, defaultValue=default_value)

                # Fallback to default value
                # when the settings value does not seem to fit the settings field.
                # This can happen when the settings data model has been changed between
                # two versions of the plugin.
                if value is None:
                    value = default_value
                elif isinstance(default_value, List) and not isinstance(value, List):
                    value = default_value

            settings_values[i.name] = value

        # instanciate new settings object
        options = PlgSettingsStructure(**settings_values)

        settings.endGroup()

        # If the plugin version has changed, save the new settings
        if options.version != __version__:
            PlgOptionsManager().save_from_object(options)

        return options

    @staticmethod
    def get_value_from_key(
        key: str, default=None, exp_type=QVariant
    ):  # Fix a faire remonter a Oslandia
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings value matching key
        """
        if not hasattr(PlgSettingsStructure(), key):
            idg.toolbelt.log_handler.PlgLogger.log(
                message="Bad settings key. Must be one of: {}".format(
                    ",".join(PlgSettingsStructure._fields)  # A fixer
                ),
                log_level=1,
            )
            return None

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            out_value = settings.value(key=key, defaultValue=default, type=exp_type)
        except Exception as err:
            idg.toolbelt.log_handler.PlgLogger.log(
                message="Error occurred trying to get settings: {}.Trace: {}".format(
                    key, err
                )
            )
            out_value = None

        settings.endGroup()

        return out_value

    @classmethod
    def set_value_from_key(cls, key: str, value) -> bool:
        """Set plugin QSettings value using the key.

        :param key: QSettings key
        :type key: str
        :param value: value to set
        :type value: depending on the settings
        :return: operation status
        :rtype: bool
        """
        if not hasattr(PlgSettingsStructure(), key):
            idg.toolbelt.log_handler.PlgLogger.log(
                message="Bad settings key. Must be one of: {}".format(
                    ",".join(PlgSettingsStructure._fields)
                ),
                log_level=2,
            )
            return False

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            settings.setValue(key, value)
            out_value = True
        except Exception as err:
            idg.toolbelt.log_handler.PlgLogger.log(
                message="Error occurred trying to set settings: {}.Trace: {}".format(
                    key, err
                )
            )
            out_value = False

        settings.endGroup()

        return out_value

    @classmethod
    def save_from_object(cls, plugin_settings_obj: PlgSettingsStructure):
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings value matching key
        """
        settings = QgsSettings()
        settings.beginGroup(__title__)

        new_settings_as_dict = asdict(plugin_settings_obj)
        new_settings_as_dict["version"] = __version__
        
        for k, v in new_settings_as_dict.items():
            cls.set_value_from_key(k, v)

        settings.endGroup()
