# -*- coding: utf-8 -*-
"""
/***************************************************************************
 shp2D3
                                 A QGIS plugin
 Convert an ESRI shapefile to 3D using a DEM
                             -------------------
        begin                : 2015-10-14
        copyright            : (C) 2015 by roberto marzocchi
        email                : roberto.marzocchi@gter.it
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load shp2D3 class from file shp2D3.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .shp2D3 import shp2D3
    return shp2D3(iface)
