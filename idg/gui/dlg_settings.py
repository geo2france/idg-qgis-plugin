#! python3  # noqa: E265

"""
Plugin settings form integrated into QGIS 'Options' menu.
"""

# standard
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.core import QgsApplication
from qgis.gui import QgsOptionsPageWidget, QgsOptionsWidgetFactory
from qgis.PyQt import uic, QtWidgets
from qgis.PyQt.Qt import QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon

# project
from idg.__about__ import (
    __icon_path__,
    __title__,
    __uri_homepage__,
    __uri_tracker__,
    __version__,
)
from idg.toolbelt import PlgLogger, PlgOptionsManager
from idg.browser.remote_platforms import RemotePlatforms
from idg.toolbelt.preferences import PlgSettingsStructure

# ############################################################################
# ########## Globals ###############
# ##################################

FORM_CLASS, _ = uic.loadUiType(
    Path(__file__).parent / "{}.ui".format(Path(__file__).stem)
)


# ############################################################################
# ########## Classes ###############
# ##################################


def tablewidgetToList(table: QtWidgets.QTableWidget, column_index: int, skipnone=True):
    """Convertir en liste une colonne d'un tableau"""
    out = []
    for row in range(table.rowCount()):
        item = table.item(row, column_index)
        if (item is None or item.text().strip() == "") and skipnone:
            continue
        out.append(item.text())
    return out


def listToTablewidget(
    data_list: list[str],
    table: QtWidgets.QTableWidget,
    column_index: int,
    skipnone=True,
):
    """Ecrit une liste dans la colonne _column_index_ d'un talbeau"""
    for row, item in enumerate(data_list):
        table.setItem(row, column_index, QtWidgets.QTableWidgetItem(str(item)))


class ConfigOptionsPage(FORM_CLASS, QgsOptionsPageWidget):
    """Settings form embedded into QGIS 'options' menu."""

    def __init__(self, parent):
        super().__init__(parent)
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()

        # load UI and set objectName
        self.setupUi(self)
        self.setObjectName("mOptionsPage{}".format(__title__))

        # header
        self.lbl_title.setText(f"{__title__} - Version {__version__}")

        # customization
        self.btn_help.setIcon(QgsApplication.getThemeIcon("mActionHelpContents.svg"))
        self.btn_help.pressed.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )

        self.btn_report.setIcon(
            QIcon(":images/themes/default/console/iconSyntaxErrorConsole.svg")
        )
        self.btn_report.pressed.connect(
            partial(QDesktopServices.openUrl, QUrl(f"{__uri_tracker__}"))
        )

        self.btn_reset.setIcon(QgsApplication.getThemeIcon("mActionUndo.svg"))
        self.btn_reset.pressed.connect(self.reset_settings)

        # Hide non operational widgets
        # todo: make them work
        self.lbl_custom_platforms.hide()
        self.tbl_platforms_list.hide()
        self.btn_add_platform.hide()

        # Custom IDGs list
        self.tbl_platforms_list.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )  # Stretch the column in order to use the full width of the table

        # Button to add a custom IDG
        self.btn_add_platform.setIcon(QgsApplication.getThemeIcon("symbologyAdd.svg"))
        self.btn_add_platform.clicked.connect(
            lambda: self.tbl_platforms_list.setRowCount(
                self.tbl_platforms_list.rowCount() + 1
            )
        )

        self.vbox = QtWidgets.QVBoxLayout()
        self.checkboxes = []
        self.groupBox_stock.setLayout(self.vbox)

        # load previously saved settings
        self.load_settings()

    def _update_default_idgs_list(self):
        self.checkboxes = []

        # Clear content of layout
        for i in reversed(range(self.vbox.count())):
            self.vbox.itemAt(i).widget().setParent(None)

        # Create checkboxes
        for pf in RemotePlatforms(read_projects=False).plateforms:
            cb = QtWidgets.QCheckBox(pf.idg_id)
            self.vbox.addWidget(cb)
            self.checkboxes.append(cb)

        # Set values to checkboxes
        settings = self.plg_settings.get_plg_settings()
        hidden_idg = settings.hidden_idgs
        for cb in self.checkboxes:
            if cb.text() in hidden_idg:
                cb.setChecked(False)
            else:
                cb.setChecked(True)

    def apply(self):
        """Called to permanently apply the settings shown in the options page (e.g. \
        save them to QgsSettings objects). This is usually called when the options \
        dialog is accepted."""
        settings = self.plg_settings.get_plg_settings()

        # Misc
        settings.version = __version__
        settings.custom_idgs = tablewidgetToList(self.tbl_platforms_list, 0)

        # Default IDG list
        hidden_idgs_arr = []
        for cb in self.checkboxes:
            print(cb.text(), cb.checkState())
            if cb.checkState() == 0:
                hidden_idgs_arr.append(cb.text())
                # Add to hidden PF
        settings.hidden_idgs = hidden_idgs_arr
        # Dump new settings into QgsSettings
        self.plg_settings.save_from_object(settings)

        if __debug__:
            self.log(
                message="DEBUG - Settings successfully saved.",
                log_level=4,
            )

        # Send signal to plugin
        self.settings_updated()

    def plugin_config_file_reloaded(self):
        self._update_default_idgs_list()

    def load_settings(self):
        """Load options from QgsSettings into UI form."""
        settings = self.plg_settings.get_plg_settings()

        # Default IDG list
        self._update_default_idgs_list()

        # Custom IDG list
        self.tbl_platforms_list.setRowCount(len(settings.custom_idgs) + 1)
        listToTablewidget(
            settings.custom_idgs, self.tbl_platforms_list, column_index=0
        )

        # Version of the plugin used to save the settings
        self.lbl_version_saved_value.setText(settings.version)

    def reset_settings(self):
        """Reset settings to default values (set in preferences.py module)."""
        default_settings = PlgSettingsStructure()

        # Dump default settings into QgsSettings
        self.plg_settings.save_from_object(default_settings)
        self.load_settings()

        # Call download function
        self.download_tree_config_file(end_slot=self.plugin_config_file_reloaded)



class PlgOptionsFactory(QgsOptionsWidgetFactory):
    """Factory for options widget."""

    def __init__(self, settings_updated=None, download_tree_config_file=None):
        """Constructor."""
        super().__init__()
        self.settings_updated = settings_updated
        self.download_tree_config_file = download_tree_config_file

    def icon(self) -> QIcon:
        """Returns plugin icon, used to as tab icon in QGIS options tab widget.

        :return: _description_
        :rtype: QIcon
        """
        return QIcon(str(__icon_path__))

    def createWidget(self, parent) -> ConfigOptionsPage:
        """Create settings widget.

        :param parent: Qt parent where to include the options page.
        :type parent: QObject

        :return: options page for tab widget
        :rtype: ConfigOptionsPage
        """
        options_page = ConfigOptionsPage(parent)

        # Plugin functions to be called on dlg_settings events
        if self.settings_updated:
            options_page.settings_updated = self.settings_updated
        if self.download_tree_config_file:
            options_page.download_tree_config_file = self.download_tree_config_file

        return options_page

    def title(self) -> str:
        """Returns plugin title, used to name the tab in QGIS options tab widget.

        :return: plugin title from about module
        :rtype: str
        """
        return __title__

    def helpId(self) -> str:
        """Returns plugin help URL.

        :return: plugin homepage url from about module
        :rtype: str
        """
        return __uri_homepage__
