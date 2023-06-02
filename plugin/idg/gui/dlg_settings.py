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
from qgis.utils import iface
from qgis.PyQt import uic, QtWidgets
from qgis.PyQt.Qt import QUrl, QWidget
from qgis.PyQt.QtGui import QDesktopServices, QIcon

# project
from idg.__about__ import (
    DIR_PLUGIN_ROOT,
    __icon_path__,
    __title__,
    __uri_homepage__,
    __uri_tracker__,
    __version__,
)
from idg.toolbelt import PlgLogger, PlgOptionsManager
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
    out=[]
    for row in range(table.rowCount()):
            item = table.item(row, column_index)
            if (item is None or item.text().strip() == '') and skipnone:
                continue
            out.append(item.text())
    return out

def listToTablewidget(data_list: list[str], table: QtWidgets.QTableWidget, column_index: int, skipnone=True):
    """ Ecrit une liste dans la colonne _column_index_ d'un talbeau"""
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
        self.btn_help.setIcon(QIcon(QgsApplication.iconPath("mActionHelpContents.svg")))
        self.btn_help.pressed.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )

        self.btn_report.setIcon(
            QIcon(QgsApplication.iconPath("console/iconSyntaxErrorConsole.svg"))
        )
        self.btn_report.pressed.connect(
            partial(QDesktopServices.openUrl, QUrl(f"{__uri_tracker__}/new/choose"))
        )

        self.btn_reset.setIcon(QIcon(QgsApplication.iconPath("mActionUndo.svg")))
        self.btn_reset.pressed.connect(self.reset_settings)

        # table widget
        self.idgs_list.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch) # Etirer la colonne à 100% du tableau
        self.btn_addrow.setIcon(QIcon(":images/themes/default/symbologyAdd.svg"))
        self.btn_addrow.clicked.connect(
            lambda:self.idgs_list.setRowCount(self.idgs_list.rowCount() + 1)
        )
        # load previously saved settings
        self.load_settings()

    def apply(self):
        """Called to permanently apply the settings shown in the options page (e.g. \
        save them to QgsSettings objects). This is usually called when the options \
        dialog is accepted."""
        settings = self.plg_settings.get_plg_settings()

        # misc
        settings.debug_mode = self.opt_debug.isChecked()
        settings.version = __version__
        settings.custom_idgs = ','.join(tablewidgetToList(self.idgs_list, 0))
        # dump new settings into QgsSettings
        self.plg_settings.save_from_object(settings) #Les variables globales ne sont peut être pas MAJ ici

        iface.mainWindow().findChildren(QWidget, 'Browser')[0].refresh() # refresh browser (supprimer et recreer le registre IDG plutôt ?)

        if __debug__:
            self.log(
                message="DEBUG - Settings successfully saved.",
                log_level=4,
            )

    def load_settings(self):
        """Load options from QgsSettings into UI form."""
        settings = self.plg_settings.get_plg_settings()
        # global
        self.opt_debug.setChecked(settings.debug_mode)
        self.lbl_version_saved_value.setText(settings.version)
        self.idgs_list.setRowCount( len(settings.custom_idgs.split(',')) + 1 )
        listToTablewidget(settings.custom_idgs.split(','), self.idgs_list, column_index=0)

    def reset_settings(self):
        """Reset settings to default values (set in preferences.py module)."""
        default_settings = PlgSettingsStructure()

        # dump default settings into QgsSettings
        self.plg_settings.save_from_object(default_settings)

        # update the form
        self.load_settings()

class PlgOptionsFactory(QgsOptionsWidgetFactory):
    """Factory for options widget."""

    def __init__(self):
        """Constructor."""        
        super().__init__()

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
        return ConfigOptionsPage(parent)

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

