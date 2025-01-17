#! python3  # noqa: E265

# standard library
import logging
from functools import partial
from typing import Callable

# PyQGIS
from qgis.core import QgsMessageLog, QgsMessageOutput
from qgis.gui import QgsMessageBar
from qgis.PyQt.QtWidgets import QPushButton, QWidget
from qgis.utils import iface

# project package
from idg.__about__ import __title__
import idg.toolbelt.preferences as plg_prefs_hdlr

# ############################################################################
# ########## Classes ###############
# ##################################


class PlgLogger(logging.Handler):
    """Python logging handler supercharged with QGIS useful methods."""

    @staticmethod
    def log(
        message: str,
        application: str = __title__,
        log_level: int = 0,
        push: bool = False,
        duration: int = None,
        # widget
        button: bool = False,
        button_text: str = None,
        button_connect: Callable = None,
        # parent
        parent_location: QWidget = None,
    ):
        """Send messages to QGIS messages windows and to the user as a message bar. \
        Plugin name is used as title. If debug mode is disabled, only warnings (1) and \
        errors (2) or with push are sent.

        :param message: message to display
        :type message: str
        :param application: name of the application sending the message. \
        Defaults to __about__.__title__
        :type application: str, optional
        :param log_level: message level. Possible values: 0 (info), 1 (warning), \
        2 (critical), 3 (success), 4 (none - grey). Defaults to 0 (info)
        :type log_level: int, optional
        :param push: also display the message in the QGIS message bar in addition to \
        the log, defaults to False
        :type push: bool, optional
        :param duration: duration of the message in seconds. If not set, the \
        duration is calculated from the log level: `(log_level + 1) * 3`. seconds. \
        If set to 0, then the message must be manually dismissed by the user. \
        Defaults to None.
        :type duration: int, optional
        :param button: display a button in the message bar. Defaults to False.
        :type button: bool, optional
        :param button_text: text label of the button. Defaults to None.
        :type button_text: str, optional
        :param button_connect: function to be called when the button is pressed. \
        If not set, a simple dialog (QgsMessageOutput) is used to dislay the message. \
        Defaults to None.
        :type button_connect: Callable, optional
        :param parent_location: parent location widget. \
        If not set, QGIS canvas message bar is used to push message, \
        otherwise if a QgsMessageBar is available in parent_location it is used instead. \
        Defaults to None.
        :type parent_location: Widget, optional

        :Example:

        .. code-block:: python

            log(message="Plugin loaded - INFO", log_level=0, push=False)
            log(message="Plugin loaded - WARNING", log_level=1, push=1, duration=5)
            log(message="Plugin loaded - ERROR", log_level=2, push=1, duration=0)
            log(
                message="Plugin loaded - SUCCESS",
                log_level=3,
                push=1,
                duration=10,
                button=True
            )
            log(message="Plugin loaded - TEST", log_level=4, push=0)
        """
        # if not debug mode and not push, let's ignore INFO, SUCCESS and TEST
        debug_mode = plg_prefs_hdlr.PlgOptionsManager.get_plg_settings().debug_mode
        if not debug_mode and not push and (log_level < 1 or log_level > 2):
            return

        # ensure message is a string
        if not isinstance(message, str):
            try:
                message = str(message)
            except Exception as err:
                err_msg = "Log message must be a string, not: {}. Trace: {}".format(
                    type(message), err
                )
                logging.error(err_msg)
                message = err_msg

        # send it to QGIS messages panel
        QgsMessageLog.logMessage(
            message=message, tag=application, notifyUser=push, level=log_level
        )

        # optionally, display message on QGIS Message bar (above the map canvas)
        if push:
            msg_bar = None

            # QGIS or custom dialog
            if parent_location and isinstance(parent_location, QWidget):
                msg_bar = parent_location.findChild(QgsMessageBar)

            if not msg_bar:
                msg_bar = iface.messageBar()

            # calc duration
            if duration is None:
                duration = (log_level + 1) * 3

            # create message with/out a widget
            if button:
                # create output message
                notification = iface.messageBar().createMessage(
                    title=application, text=message
                )
                widget_button = QPushButton(button_text or "More…")
                if button_connect:
                    widget_button.clicked.connect(button_connect)
                else:
                    mini_dlg = QgsMessageOutput.createMessageOutput()
                    mini_dlg.setTitle(application)
                    mini_dlg.setMessage(message, QgsMessageOutput.MessageText)
                    widget_button.clicked.connect(partial(mini_dlg.showMessage, False))

                notification.layout().addWidget(widget_button)
                msg_bar.pushWidget(
                    widget=notification, level=log_level, duration=duration
                )

            else:
                # send simple message
                msg_bar.pushMessage(
                    title=application,
                    text=message,
                    level=log_level,
                    duration=duration,
                )
