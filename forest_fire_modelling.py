# -*- coding: utf-8 -*-
"""
/***************************************************************************
 forest_fire_modelling
                                 A QGIS plugin
 forest fire modelling
                              -------------------
        begin                : 2017-09-19
        git sha              : $Format:%H$
        copyright            : (C) 2017 by balaji
        email                : balaji.9th@gmail.com
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from forest_fire_modelling_dialog import forest_fire_modellingDialog
import os.path
from process import *


class forest_fire_modelling:
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
            'forest_fire_modelling_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&forest_fire_modelling')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'forest_fire_modelling')
        self.toolbar.setObjectName(u'forest_fire_modelling')

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
        return QCoreApplication.translate('forest_fire_modelling', message)


    def add_action(
        self,
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
        self.dlg = forest_fire_modellingDialog()

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

        icon_path = ':/plugins/forest_fire_modelling/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'forest fire model'),
            callback=self.run,
            parent=self.iface.mainWindow())
        QObject.connect(self.dlg.dem_btn,SIGNAL("clicked()"),self.Browseinputfiledem)
        QObject.connect(self.dlg.green_btn,SIGNAL("clicked()"),self.Browseinputfilegreen)
        QObject.connect(self.dlg.red_btn,SIGNAL("clicked()"),self.Browseinputfilered)
        QObject.connect(self.dlg.nir_btn,SIGNAL("clicked()"),self.Browseinputfilenir)
        QObject.connect(self.dlg.swir_btn,SIGNAL("clicked()"),self.Browseinputfileswir)
        QObject.connect(self.dlg.shape_file_btn,SIGNAL("clicked()"),self.Browseinputfileshape)
        QObject.connect(self.dlg.output_dir_btn,SIGNAL("clicked()"),self.Browseoutputfolder)
        QObject.connect(self.dlg.burnt_btn,SIGNAL("clicked()"),self.Browseburnt)

        self.dlg.time_step.valueChanged.connect(self.step_changed)
        self.dlg.dateTimeEdit.dateTimeChanged.connect(self.step_changed)
        self.dlg.speed.textChanged.connect(self.step_changed)
        
        QObject.connect(self.dlg.ok,SIGNAL("clicked()"),self.go)
        QObject.connect(self.dlg.cancel,SIGNAL("clicked()"),self.close)
        print "a"

    
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&forest_fire_modelling'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

        
    def Browseinputfiledem(self):
        fd=QFileDialog()
        fd.setFileMode(QFileDialog.ExistingFile)
        ext_names=list()
        ext_names.append("*.TIFF *.TIF *.tif *.tiff")
        fd.setFilters(ext_names)
        filenames = list()		
        if fd.exec_():
            filenames = fd.selectedFiles()
            self.dlg.dem.setText(filenames[0])      
            self.dem_file=filenames[0]
            
    def Browseinputfilered(self):
        fd=QFileDialog()
        fd.setFileMode(QFileDialog.ExistingFile)
        ext_names=list()
        ext_names.append("*.TIFF *.TIF *.tif *.tiff")
        fd.setFilters(ext_names)
        filenames = list()		
        if fd.exec_():
            filenames = fd.selectedFiles()
            self.dlg.red.setText(filenames[0])      
            self.red_file=filenames[0]

    def Browseburnt(self):
        fd=QFileDialog()
        fd.setFileMode(QFileDialog.ExistingFile)
        ext_names=list()
        ext_names.append("*.TIFF *.TIF *.tif *.tiff")
        fd.setFilters(ext_names)
        filenames = list()      
        if fd.exec_():
            filenames = fd.selectedFiles()
            self.dlg.burnt.setText(filenames[0])      
            self.burnt_file=filenames[0]
            
    def Browseinputfilegreen(self):
        fd=QFileDialog()
        fd.setFileMode(QFileDialog.ExistingFile)
        ext_names=list()
        ext_names.append("*.TIFF *.TIF *.tif *.tiff")
        fd.setFilters(ext_names)
        filenames = list()		
        if fd.exec_():
            filenames = fd.selectedFiles()
            self.dlg.green.setText(filenames[0])      
            self.green_file=filenames[0]

    def Browseinputfileshape(self):
        fd=QFileDialog()
        fd.setFileMode(QFileDialog.ExistingFile)
        ext_names=list()
        ext_names.append("*.SHP *.shp")
        fd.setFilters(ext_names)
        filenames = list()      
        if fd.exec_():
            filenames = fd.selectedFiles()
            self.dlg.shape_file.setText(filenames[0])      
            self.shape_file=filenames[0]
            
    def Browseinputfilenir(self):
        fd=QFileDialog()
        fd.setFileMode(QFileDialog.ExistingFile)
        ext_names=list()
        ext_names.append("*.TIFF *.TIF *.tif *.tiff")
        fd.setFilters(ext_names)
        filenames = list()		
        if fd.exec_():
            filenames = fd.selectedFiles()
            self.dlg.nir.setText(filenames[0])      
            self.nir_file=filenames[0]
            
    def Browseinputfileswir(self):
        fd=QFileDialog()
        fd.setFileMode(QFileDialog.ExistingFile)
        ext_names=list()
        ext_names.append("*.TIFF *.TIF *.tif *.tiff")
        fd.setFilters(ext_names)
        filenames = list()		
        if fd.exec_():
            filenames = fd.selectedFiles()
            self.dlg.swir.setText(filenames[0])      
            self.swir_file=filenames[0]
            
    def Browseoutputfolder(self):
        fd=QFileDialog()
        fd.setFileMode(QFileDialog.Directory)
        
        filenames = list()		
        if fd.exec_():
            filenames = fd.selectedFiles()
            self.dlg.output_dir.setText(filenames[0])  
            self.output_dir=filenames[0]
            
    def read_all(self):
        self.output_dir=self.dlg.output_dir.text()
        self.dem_file=self.dlg.dem.text()
        self.green_file=self.dlg.green.text()
        self.red_file=self.dlg.red.text()
        self.nir_file=self.dlg.nir.text()
        self.swir_file=self.dlg.swir.text()
        self.shape_file=self.dlg.shape_file.text()
        self.burnt_file=self.dlg.burnt.text()
        self.ndvi=float(self.dlg.ndvi.text())
        self.time_step=int(self.dlg.time_step.text())
        self.velocity=float(self.dlg.speed.text())

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
    
    def close(self):
        self.dlg.done(0) 
        
    def go(self):
        progdialog = QProgressDialog("Processing...","Cancel", 0, 101,self.dlg)
        progdialog.setWindowTitle("Processing")
        self.read_all()
        progdialog.setValue(0)
        progdialog.setLabelText("calling algorithm")
        
        progdialog.setWindowModality(Qt.WindowModal)
        progdialog.show()
        run_code(self.dem_file,self.green_file,self.red_file,self.nir_file,self.swir_file,self.output_dir,self.ndvi,progdialog,self.time_step,self.shape_file,self.burnt_file)
    
    def compute_date(self,steps,velocity,start_date):
        pix=30
        sec=((pix*36000)/(velocity*1000))*steps
        start_date=start_date.addSecs(sec)
        self.dlg.dateTimeEdit1.setDate(start_date.date())
        
        self.dlg.dateTimeEdit1.setDateTime(start_date)

        print start_date

    

    def step_changed(self):
            print "asas"
            steps=int(self.dlg.time_step.text())
            velocity=float(self.dlg.speed.text())
            start_date=self.dlg.dateTimeEdit.dateTime()
            self.compute_date(steps,velocity,start_date)     