# -*- coding: utf-8 -*-
"""Module containing the setup for the dockwidget."""

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dockwidget.ui'))


class LizardViewerDockWidget(QtGui.QDockWidget, FORM_CLASS):
    """Module for creating the dockwidget."""

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(LizardViewerDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def closeEvent(self, event):
        """Module for closing the dockwidget."""
        self.closingPlugin.emit()
        event.accept()

    def change_tab(self, string):
        """Function to dynamically change tabs."""
        if string == "Log in":
            self.tabWidget.setCurrentIndex(0)
        elif string == "Select data":
            self.tabWidget.setCurrentIndex(1)
        elif string == "Uploaden":
            self.tabWidget.setCurrentIndex(2)

    def set_all_status_bars_text(self, string):
        """Set the text for the status bars."""
        status_bars = self.all_status_bars()
        for status_bar in status_bars:
            status_bar.setText(string)
            status_bar.repaint()

    def all_status_bars(self):
        """Function to return all the status bars."""
        return [self.status_bar_log_in,
                self.status_bar_select_data,
                self.status_bar_upload_data]
