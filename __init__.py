# -*- coding: utf-8 -*-

"""
***************************************************************************
* Plugin Name: Bearing Protractor
* Version    : 3.9.2
* Author     : Jujun Junaedi
* Email      : jujun.junaedi@outlook.com
* Description: QGIS Floating Planning Tool for Azimuth & Distance
* License    : GPL-2.0-or-later
* Motto      : "Sebaik-baiknya Manusia adalah yang bermanfaat bagi sesama"
***************************************************************************
"""

def classFactory(iface):
    """
    Load the BearingProtractorPlugin class from the bearing_protractor_plugin module.
    
    :param iface: A reference to the QGIS desktop interface.
    :type iface: qgis.gui.QgisInterface
    """
    from .bearing_protractor_plugin import BearingProtractorPlugin
    return BearingProtractorPlugin(iface)