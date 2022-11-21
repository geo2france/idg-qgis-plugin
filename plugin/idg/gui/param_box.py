# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QCheckBox
from qgis.PyQt.QtWidgets import QDialogButtonBox, QMessageBox, QDialog
from qgis.PyQt.QtCore import Qt
from qgis.core import *
from qgis.gui import *

from idg.toolbelt import PluginGlobals
from idg.toolbelt.tree_node_factory import TreeNodeFactory, download_tree_config_file


class ParamBox(QDialog):
    """
    Param box of the plugin
    """

    def __init__(self, parent=None, tree_dock=None):
        QWidget.__init__(self, parent)
        self.tree_dock = tree_dock

        # Init GUI
        self.init_gui()

        # Evaluate flags and tupdate the state of the Apply button
        self.evaluate_flags()

    def init_gui(self):
        """
        """
        dlg_layout = QVBoxLayout()
        params_layout = QVBoxLayout()
        params_layout.setAlignment(Qt.AlignTop)

        # Config files groupbox
        self.config_files_groupbox = QgsCollapsibleGroupBox(u"Fichier de configuration de l'arbre des ressources")
        config_file_groupbox_layout = QFormLayout(self.config_files_groupbox)

        # URL of the file
        self.config_file_url_label = QLabel(u"URL du fichier", self)
        self.config_file_url_edit = QLineEdit(self)
        self.config_file_url_edit.editingFinished.connect(self.config_file_url_changed)
        config_file_groupbox_layout.addRow(self.config_file_url_label, self.config_file_url_edit)

        # Download the file at startup
        self.download_cb = QCheckBox(u"Télécharger le fichier à chaque lancement de QGIS", self)
        self.download_cb.stateChanged.connect(self.download_cb_changed)
        config_file_groupbox_layout.addRow(self.download_cb)

        params_layout.addWidget(self.config_files_groupbox)

        # Download the file now
        self.download_now_label = QLabel(u"Télécharger le fichier maintenant", self)
        self.download_now_btnbox = QDialogButtonBox()
        self.download_now_btnbox.setOrientation(Qt.Horizontal)
        self.download_now_btnbox.setStandardButtons(QDialogButtonBox.Yes)
        self.download_now_btnbox.button(QDialogButtonBox.Yes).clicked.connect(self.download_file_now)
        config_file_groupbox_layout.addRow(self.download_now_label, self.download_now_btnbox)

        # Content of the resource tree groupbox
        self.resource_tree_groupbox = QgsCollapsibleGroupBox(u"Contenu de l'arbre des ressources")
        resource_tree_groupbox_layout = QFormLayout(self.resource_tree_groupbox)

        # Hide resources with a warn flag
        self.hide_resources_with_warn_status_cb = QCheckBox(u"Masquer les ressources en cours d'intégration", self)
        self.hide_resources_with_warn_status_cb.stateChanged.connect(self.hide_resources_with_warn_cb_changed)
        resource_tree_groupbox_layout.addRow(self.hide_resources_with_warn_status_cb)

        # Hide empty groups in the resources tree
        self.hide_empty_groups_cb = QCheckBox(u"Masquer les groupes de ressources vides", self)
        self.hide_empty_groups_cb.stateChanged.connect(self.hide_empty_groups_cb_changed)
        resource_tree_groupbox_layout.addRow(self.hide_empty_groups_cb)

        params_layout.addWidget(self.resource_tree_groupbox)
        dlg_layout.addLayout(params_layout)

        # Set values
        self.set_values_from_qsettings()

        # Bottom dialog buttons
        self.button_box = QDialogButtonBox()
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(
            QDialogButtonBox.RestoreDefaults|QDialogButtonBox.Apply|QDialogButtonBox.Close)
        self.button_box.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.restore_defaults_button_clicked)
        self.button_box.button(QDialogButtonBox.Close).clicked.connect(self.close_button_clicked)
        self.button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_button_clicked)

        # Dialog box title, layout, size and display
        title = u"Paramétrage de l'extension Géo2France…"
        self.setWindowTitle(title)
        dlg_layout.addWidget(self.button_box)
        self.setLayout(dlg_layout)
        self.setMinimumWidth(500)
        self.resize(self.sizeHint())
        self.setSizeGripEnabled(False)
        self.setFixedSize(self.size())
        self.show()
        self.setSizeGripEnabled(False)

    def set_values_from_qsettings(self):
        """
        """
        # URL of the file
        self.config_file_url_edit.blockSignals(True)
        self.config_file_url_edit.setText(PluginGlobals.instance().CONFIG_FILE_URLS[0])
        self.config_file_url_edit.setCursorPosition(0)
        self.config_file_url_edit.blockSignals(False)

        # Download the file at startup
        self.download_cb.blockSignals(True)
        self.download_cb.setChecked(PluginGlobals.instance().CONFIG_FILES_DOWNLOAD_AT_STARTUP)
        self.download_cb.blockSignals(False)

        # Hide resources with a warn flag
        self.hide_resources_with_warn_status_cb.blockSignals(True)
        self.hide_resources_with_warn_status_cb.setChecked(PluginGlobals.instance().HIDE_RESOURCES_WITH_WARN_STATUS)
        self.hide_resources_with_warn_status_cb.blockSignals(False)

        # Hide empty groups in the resources tree
        self.hide_empty_groups_cb.blockSignals(True)
        self.hide_empty_groups_cb.setChecked(PluginGlobals.instance().HIDE_EMPTY_GROUPS)
        self.hide_empty_groups_cb.blockSignals(False)

    def evaluate_flags(self):
        """
        """
        # Detect modifications
        file_url_changed = (self.config_file_url_edit.text() != PluginGlobals.instance().CONFIG_FILE_URLS[0])

        download_at_startup_changed = \
            (self.download_cb.isChecked() != PluginGlobals.instance().CONFIG_FILES_DOWNLOAD_AT_STARTUP)

        hide_resources_with_warn_status_changed = \
            (self.hide_resources_with_warn_status_cb.isChecked() !=
             PluginGlobals.instance().HIDE_RESOURCES_WITH_WARN_STATUS)

        hide_empty_groups_changed = \
            (self.hide_empty_groups_cb.isChecked() != PluginGlobals.instance().HIDE_EMPTY_GROUPS)

        # Init flags
        self.need_update_visibility_of_tree_items = hide_empty_groups_changed or hide_resources_with_warn_status_changed
        self.need_update_of_tree_content = file_url_changed
        self.need_save = file_url_changed or download_at_startup_changed or \
                         hide_resources_with_warn_status_changed or \
                         hide_empty_groups_changed

        # Update state of the Apply Button
        self.button_box.button(QDialogButtonBox.Apply).setEnabled(self.need_save)

    def download_cb_changed(self, state):
        """
        Event sent when the state of the checkbox change
        """
        self.evaluate_flags()

    def config_file_url_changed(self):
        """
        Event sent when the text of the line edit has been edited
        """
        self.evaluate_flags()

    def hide_resources_with_warn_cb_changed(self, state):
        """
        Event sent when the state of the checkbox change
        """
        self.evaluate_flags()

    def hide_empty_groups_cb_changed(self, state):
        """
        Event sent when the state of the checkbox change
        """
        self.evaluate_flags()

    def download_file_now(self):
        """
        """
        # Download, read the resources tree file and update the GUI
        download_tree_config_file(self.config_file_url_edit.text())
        self.ressources_tree = TreeNodeFactory(PluginGlobals.instance().config_file_path).root_node
        if self.tree_dock is not None:
            self.tree_dock.set_tree_content(self.ressources_tree)

    def save_settings(self):
        """
        """
        # URL of the file
        new_value = [self.config_file_url_edit.text()]
        PluginGlobals.instance().set_qgis_settings_value("config_file_urls", new_value)

        # Download the file at startup
        new_value = self.download_cb.isChecked()
        PluginGlobals.instance().set_qgis_settings_value("config_files_download_at_startup", new_value)

        # Hide resources with a warn flag
        new_value = self.hide_resources_with_warn_status_cb.isChecked()
        PluginGlobals.instance().set_qgis_settings_value("hide_resources_with_warn_status", new_value)

        # Hide empty groups in the resources tree
        new_value = self.hide_empty_groups_cb.isChecked()
        PluginGlobals.instance().set_qgis_settings_value("hide_empty_groups", new_value)

        # Download, read the resources tree file and update the GUI
        if self.need_update_of_tree_content:
            download_tree_config_file(PluginGlobals.instance().CONFIG_FILE_URLS[0])
            self.ressources_tree = TreeNodeFactory(PluginGlobals.instance().config_file_path).root_node
            self.tree_dock.set_tree_content(self.ressources_tree)

        # Update the visibility of tree items
        elif self.need_update_visibility_of_tree_items and self.tree_dock is not None:
            self.tree_dock.update_visibility_of_tree_items()

    def apply_button_clicked(self):
        """
        """
        self.save_settings()
        self.evaluate_flags()

    def close_button_clicked(self):
        """
        """
        self.close()

    def restore_defaults_button_clicked(self):
        """
        """
        # URL of the file
        self.config_file_url_edit.blockSignals(True)
        self.config_file_url_edit.setText(PluginGlobals.instance().get_qgis_setting_default_value(
            "CONFIG_FILE_URLS")[0])
        self.config_file_url_edit.setCursorPosition(0)
        self.config_file_url_edit.blockSignals(False)

        # Download the file at startup
        self.download_cb.blockSignals(True)
        self.download_cb.setChecked(PluginGlobals.instance().get_qgis_setting_default_value(
            "CONFIG_FILES_DOWNLOAD_AT_STARTUP"))
        self.download_cb.blockSignals(False)

        # Hide resources with a warn flag
        self.hide_resources_with_warn_status_cb.blockSignals(True)
        self.hide_resources_with_warn_status_cb.setChecked(PluginGlobals.instance().get_qgis_setting_default_value(
            "HIDE_RESOURCES_WITH_WARN_STATUS"))
        self.hide_resources_with_warn_status_cb.blockSignals(False)

        # Hide empty groups in the resources tree
        self.hide_empty_groups_cb.blockSignals(True)
        self.hide_empty_groups_cb.setChecked(PluginGlobals.instance().get_qgis_setting_default_value(
            "HIDE_EMPTY_GROUPS"))
        self.hide_empty_groups_cb.blockSignals(False)

        self.evaluate_flags()

    def closeEvent(self, evnt):
        """
        """

        if self.need_save:
            reply = QMessageBox.question(
                self,
                u"Sauvegarder ?",
                u"Voulez-vous appliquer les changements avant de fermer la fenêtre de paramétrage de l'extension ?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)

            if reply == QMessageBox.No:
                evnt.accept()
                super(ParamBox, self).closeEvent(evnt)
            elif reply == QMessageBox.Yes:
                self.save_settings()
                evnt.accept()
                super(ParamBox, self).closeEvent(evnt)

        else:
            evnt.accept()
            super(ParamBox, self).closeEvent(evnt)

        evnt.ignore()
