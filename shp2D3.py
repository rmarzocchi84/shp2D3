# -*- coding: utf-8 -*-
"""
/***************************************************************************
 shp2D3
                                 A QGIS plugin
 Convert an ESRI shapefile to 3D using a DEM
                              -------------------
        begin                : 2015-10-14
        git sha              : $Format:%H$
        copyright            : (C) 2015 by roberto marzocchi
        email                : roberto.marzocchi@gter.it
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

from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
#from PyQt4.QtGui import QAction, QIcon
from qgis.core import *
from qgis.gui import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from shp2D3_dialog import shp2D3Dialog
import os.path
import os
import string 
import shutil 



import shapefile
#import gdal
#from gdalconst import * 
from osgeo import gdal,ogr
import struct



class shp2D3:
    """QGIS Plugin Implementation."""


    def select_input_shp(self):
        filter = "ESRI Shapefile (*.shp)"
        filename = QFileDialog.getOpenFileName(self.dlg, "Select input 2D shapfile ","", filter)
        self.dlg.shp_in.setText(filename)


    def select_input_raster(self):
		filename2 = QFileDialog.getOpenFileName(self.dlg, "Select input gdal file ","", '*.tif')
		self.dlg.gdal_in.setText(filename2)



    def select_output_shp(self):
        filter = "ESRI Shapefile (*.shp)"
        #QString filePath = QFileDialog::getSaveFileName(GetQtMainFrame(), tr("Save Worksheet"), defaultDir, filter, &filter);
        filename3 = QFileDialog.getSaveFileName(self.dlg, "Select output file ",".shp", filter)
        self.dlg.shp_out.setText(filename3)


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
            'shp2D3_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = shp2D3Dialog()



        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&shp2D3')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'shp2D3')
        self.toolbar.setObjectName(u'shp2D3')

        self.dlg.shp_in.clear()
        self.dlg.pushButton.clicked.connect(self.select_input_shp)


        self.dlg.gdal_in.clear()
        self.dlg.pushButton_2.clicked.connect(self.select_input_raster)


        self.dlg.shp_out.clear()
        self.dlg.pushButton_3.clicked.connect(self.select_output_shp)




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
        return QCoreApplication.translate('shp2D3', message)


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
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/shp2D3/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'shp2D3'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&shp2D3'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


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
            #Name of input and output files
            #output_file = open("/home/roberto/log_plugin.txt", 'w')
            #output_file.write("0 test\n")
            
            
            text_shp = self.dlg.shp_in.text()
            src_filename = self.dlg.gdal_in.text()
            shp3 = self.dlg.shp_out.text()

            if not shp3 and not src_filename and not text_shp :
                text_dbf = text_shp.replace(".shp", ".dbf")
                text_prj = text_shp.replace(".shp", ".prj") 
                myshp = open(text_shp, 'rb')
                mydbf = open(text_dbf, 'rb')

                #filename = self.dlg.lineEdit.text()
                #output_file.write("1 test\n")
                #iface.messageBar().pushInfo(u'My Plugin says', u'Hey there1')
                src_ds=gdal.Open(src_filename) 
                gt=src_ds.GetGeoTransform()
                rb=src_ds.GetRasterBand(1)
                #output_file.write(text_shp)
                #output_file.write("\n")
                #output_file.write(str(shp3))
                #output_file.write("\n1bis test\n")
                #sf = shapefile.Reader("%s" % text_shp)
                #sf = shapefile.Reader("/home/roberto/vector_elevation/linea2d.shp")
                sf = shapefile.Reader(shp=myshp, dbf=mydbf)
                #quit()


                # Create a new shapefile in memory
                w = shapefile.Writer(shapeType=shapefile.POLYLINEZ)
                #output_file.write("2 test\n")

                linea=[]
                shapes = sf.shapes()
                for shape in shapes:
                    for vertex in shape.points:
                        #print vertex
                        geometria=[]        
                        geometria.append(vertex[0])
                        geometria.append(vertex[1])
                        mx,my=vertex[0], vertex[1]  #coord in map units
                        #Convert from map to pixel coordinates.
                        #Only works for geotransforms with no rotation.
                        #If raster is rotated, see http://code.google.com/p/metageta/source/browse/trunk/metageta/geometry.py#493
                        px = int((mx - gt[0]) / gt[1]) #x pixel
                        py = int((my - gt[3]) / gt[5]) #y pixel
                        intval=rb.ReadAsArray(px,py,1,1)
                        #print intval[0] 
                        geometria.append(float(intval[0]))
                        linea.append(geometria)

                linea2=[]
                linea2.append(linea)
                #print str(linea2)

                w.line(shapeType=13, parts=linea2)

                #output_file.write("3\n")
                
                # Copy over the existing fields
                w.fields = list(sf.fields)

                # Add our new field using the pyshp API
                #w.field("ELE", "N", 7, 2)

                # We'll create a counter in this example
                # to give us sample data to add to the records
                # so we know the field is working correctly.
                i=1

                # Loop through each record, add a column.  We'll
                # insert our sample data but you could also just
                # insert a blank string or NULL DATA number
                # as a place holder
                for rec in sf.records():
                    rec.append(i)
                    i+=1

                # Add the modified record to the new shapefile 
                w.records.append(rec)

                # Copy over the geometry without any changes
                #w._shapes.extend(sf.shapes(),shapeType=shapefile.POLYLINEZ)

                # Save as a new shapefile (or write over the old one)
                w.save(shp3)
                #output_file.write("salvato\n")
                #output_file.write(text_prj)
                #output_file.write("4\n")
                #iface.messageBar().pushInfo(u'My Plugin says', u'Hey there2')

                if os.path.isfile(text_prj):  
                    # ok, esiste
                    #output_file.write("esiste\n")
                    #string.find(shp3,".shp")
                    if string.find(shp3,".shp")>0:
                        dst = shp3.replace(".shp", ".prj")
                    else:
                        dst="%s.prj" % shp3
                    #output_file.write("4 bis\n")
                    shutil.copyfile(text_prj, dst)
                #else:  
                    # no prj file input
                    #print "cazzarola"
                #output_file.write("5 fine\n")
                self.iface.messageBar().pushInfo(u'Finish', u'Shapefile 3D correctly exported')
                #output_file.write("messaggio\n")
            else :
                self.iface.messageBar().pushMessage("Error", "problem with input", level=QgsMessageBar.CRITICAL)
            pass
