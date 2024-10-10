"""
Plugin actions.
"""

from qgis.PyQt.QtWidgets import QAction


class PluginActions:
    """Container for plugin actions shared in several places of the plugin."""

    action_show_help: QAction
    action_show_settings: QAction
    action_reload_idgs: QAction
