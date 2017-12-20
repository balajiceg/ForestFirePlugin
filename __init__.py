# -*- coding: utf-8 -*-
"""
/***************************************************************************
 forest_fire_modelling
                                 A QGIS plugin
 forest fire modelling
                             -------------------
        begin                : 2017-09-19
        copyright            : (C) 2017 by balaji
        email                : balaji.9th@gmail.com
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
    """Load forest_fire_modelling class from file forest_fire_modelling.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .forest_fire_modelling import forest_fire_modelling
    return forest_fire_modelling(iface)
