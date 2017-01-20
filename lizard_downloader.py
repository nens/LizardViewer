# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LizardDownloader
                                 A QGIS plugin
 This plug-in helps with downloading data fromLizard in QGIS.
                              -------------------
        begin                : 2017-01-11
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Madeleine van Winkel
        email                : madeleine.vanwinkel@nelen-schuurmans.nl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

# Import
import os.path

from PyQt4.QtCore import QCoreApplication, QSettings, QTranslator, QVariant

from PyQt4.QtCore import qVersion

from PyQt4.QtGui import QAction, QIcon

# Import the code for the dialog
from lizard_downloader_dialog import LizardDownloaderDialog

from qgis.core import QgsFeature, QgsField, QgsGeometry, QgsPoint

from qgis.core import QgsMapLayerRegistry, QgsVectorLayer

import requests
# Initialize Qt resources from file resources.py
import resources


class LizardDownloader:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'LizardDownloader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = LizardDownloaderDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Lizard Viewer')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'LizardDownloader')
        self.toolbar.setObjectName(u'LizardDownloader')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('LizardDownloader', message)

    def add_action(self,
                   icon_path,
                   text,
                   callback,
                   enabled_flag=True,
                   add_to_menu=True,
                   add_to_toolbar=True,
                   status_tip=None,
                   whats_this=None,
                   parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = LizardDownloaderDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/LizardDownloader/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Lizard Viewer'),
            callback=self.run_downloader,
            add_to_toolbar=True,
            parent=self.iface.mainWindow())

        # Connect the downloadButton with the show_data() function
        self.dlg.downloadButton.clicked.connect(self.show_data)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Lizard Viewer'),
                action)
            self.iface.removeToolBarIcon(action)
        # Remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""
        # Show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def run_downloader(self):
        """ Show the download GUI """
        # Show the dialog
        self.dlg.show()

    def show_data(self):
        """ Show the data as a new layer on the map """

        # Setup
        WGS84 = "EPSG:4326"
        asset_types = ["pumpstations"]
        geometry_type = "Point"

        # Get the JSON containing the data from the Lizard API
        url = "https://ggmn.lizard.net/api/v2/{}/".format(asset_types[0])
        results = requests.get(url).json()["results"]

        # Create a new memory vector layer
        self.layer = QgsVectorLayer(
            "{}?crs={}".format(geometry_type, WGS84), asset_types[0], "memory")
        QgsMapLayerRegistry.instance().addMapLayer(self.layer)

        # Add attributes to the layer
        fields = [QgsField(attr, QVariant.String) for attr in results[
            0] if attr != "geometry"]
        self.layer.dataProvider().addAttributes(fields)
        self.layer.updateFields()

        # Create the feature(s)
        self.layer.startEditing()
        features = []
        for result in results:
            feature = QgsFeature(self.layer.pendingFields())
            geometry = result.pop("geometry")
            lat = float(geometry['coordinates'][0])
            lon = float(geometry['coordinates'][1])
            feature.setGeometry(QgsGeometry.fromPoint(QgsPoint(lat, lon)))
            for attribute, value in result.iteritems():
                feature.setAttribute(attribute, value)
            features.append(feature)

        # Add the features to the layer
        self.layer.dataProvider().addFeatures(features)

        self.layer.commitChanges()

        # Close the lizard_downloader_dialog
        self.dlg.close()
