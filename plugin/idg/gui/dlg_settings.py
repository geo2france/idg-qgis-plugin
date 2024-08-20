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
from qgis.PyQt.QtCore import pyqtSignal

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
from idg.browser.browser import IdgProvider
from idg.browser.tree_node_factory import DownloadAllIdgFilesAsync
from idg.plugin_globals import PluginGlobals
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

    settings_updated = pyqtSignal()

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
        self.btn_help.setIcon(QIcon(QgsApplication.iconPath("mActionHelpContents.svg")))
        self.btn_help.pressed.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )

        self.btn_report.setIcon(
            QIcon(QgsApplication.iconPath("console/iconSyntaxErrorConsole.svg"))
        )
        self.btn_report.pressed.connect(
            partial(QDesktopServices.openUrl, QUrl(f"{__uri_tracker__}"))
        )

        self.btn_reset.setIcon(QIcon(QgsApplication.iconPath("mActionUndo.svg")))
        self.btn_reset.pressed.connect(self.reset_settings)

        # table widget
        self.idgs_list.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )  # Etirer la colonne à 100% du tableau
        self.btn_addrow.setIcon(QIcon(":images/themes/default/symbologyAdd.svg"))
        self.btn_addrow.clicked.connect(
            lambda: self.idgs_list.setRowCount(self.idgs_list.rowCount() + 1)
        )

        # Lire la config pour voir quels sont les PF masquées
        self.vbox = QtWidgets.QVBoxLayout()
        self.checkboxes = []
        self.groupBox_stock.setLayout(self.vbox)
        for k in RemotePlatforms(read_projects=False).stock_idgs.keys():
            cb = QtWidgets.QCheckBox(k)
            self.vbox.addWidget(cb)
            self.checkboxes.append(cb)

        # load previously saved settings
        self.load_settings()

    def apply(self):
        """Called to permanently apply the settings shown in the options page (e.g. \
        save them to QgsSettings objects). This is usually called when the options \
        dialog is accepted."""
        settings = self.plg_settings.get_plg_settings()

        # misc
        settings.version = __version__
        settings.custom_idgs = ",".join(tablewidgetToList(self.idgs_list, 0))

        hidden__idgs_arr = []
        for cb in self.checkboxes:
            print(cb.text(), cb.checkState())
            if cb.checkState() == 0:
                hidden__idgs_arr.append(cb.text())
                # Add to hidden PF
        settings.hidden_idgs = ",".join(hidden__idgs_arr)

        # dump new settings into QgsSettings
        self.plg_settings.save_from_object(
            settings
        )  # Les variables globales ne sont peut être pas MAJ ici

        if __debug__:
            self.log(
                message="DEBUG - Settings successfully saved.",
                log_level=4,
            )

        self.settings_updated.emit()

    def load_settings(self):
        """Load options from QgsSettings into UI form."""
        settings = self.plg_settings.get_plg_settings()

        # Hidden IDGs
        hidden_idg = settings.hidden_idgs.split(",")
        for c in self.checkboxes:
            if c.text() in hidden_idg:
                c.setChecked(False)
            else:
                c.setChecked(True)
        self.idgs_list.setRowCount(len(settings.custom_idgs.split(",")) + 1)
        listToTablewidget(
            settings.custom_idgs.split(","), self.idgs_list, column_index=0
        )

        # Verison of the plugin used to save the settings
        self.lbl_version_saved_value.setText(settings.version)

    def reset_settings(self):
        """Reset settings to default values (set in preferences.py module)."""
        default_settings = PlgSettingsStructure()

        # dump default settings into QgsSettings
        self.plg_settings.save_from_object(default_settings)
        self.load_settings()
        provider = (
            QgsApplication.instance()
            .dataItemProviderRegistry()
            .provider(PluginGlobals.BROWSER_PROVIDER_NAME)
        )
        provider.root.refresh()


class PlgOptionsFactory(QgsOptionsWidgetFactory):
    """Factory for options widget."""

    def __init__(self, settings_updated_receiver=None):
        """Constructor."""
        super().__init__()
        self.settings_updated_receiver = settings_updated_receiver

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
        if self.settings_updated_receiver:
            options_page.settings_updated.connect(self.settings_updated_receiver)
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
