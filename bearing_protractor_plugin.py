#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
#  Bearing Protractor - QGIS Floating Planning Tool
# --------------------------------------------------------------------------
#  PLUGIN NAME : Bearing Protractor
#  DESCRIPTION : Floating interactive protractor for RF planning & audit, Features real-time distance tracking & multi-sector support.
#  AUTHOR      : Jujun Junaedi
#  EMAIL       : jujun.junaedi@outlook.com
#  VERSION     : 3.9.0
#  COPYRIGHT   : (c) 2024 by Jujun Junaedi
#  LICENSE     : GPL-2.0-or-later
#  MOTTO       : "Sebaik-baiknya Manusia adalah yang bermanfaat bagi sesama"
# --------------------------------------------------------------------------

"""
***************************************************************************
* Plugin Name: Bearing Protractor
* Version    : 3.9.0
* Author     : Jujun Junaedi
* Email      : jujun.junaedi@outlook.com
* Description: QGIS Floating Planning Tool for Azimuth & Distance
* License    : GPL-2.0-or-later
* Motto      : "Sebaik-baiknya Manusia adalah yang bermanfaat bagi sesama"
***************************************************************************
"""

import os

# Import UI Components
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QVariant, Qt

# Import QGIS Core Libraries
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsField,
    QgsSingleSymbolRenderer,
    QgsLineSymbol
)


class BearingProtractorPlugin:
    """
    Main class for the Bearing Protractor QGIS plugin.
    Handles initialization, UI setup in QGIS, and global layer generation.
    """

    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.plugin_dir = os.path.dirname(__file__)

        # State variables
        self.widget = None
        self.action = None
        self.about_action = None

    # ==========================================
    # Plugin Initialization & UI Hook
    # ==========================================
    def initGui(self):
        """Set up the plugin menu and toolbar icons in QGIS."""
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()

        # Main Toggle Action
        self.action = QAction(icon, "Bearing Protractor", self.iface.mainWindow())
        self.action.setCheckable(True)
        self.action.triggered.connect(self.run)

        # About Menu Action
        self.about_action = QAction("About Bearing Protractor", self.iface.mainWindow())
        self.about_action.triggered.connect(self.show_about)

        # Add to QGIS UI Menus & Toolbars
        self.iface.addPluginToMenu("&Bearing Protractor", self.action)
        self.iface.addPluginToMenu("&Bearing Protractor", self.about_action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        """Clean up the plugin UI when disabled or uninstalled."""
        if self.widget:
            self.widget.close()

        self.iface.removePluginMenu("&Bearing Protractor", self.action)
        self.iface.removePluginMenu("&Bearing Protractor", self.about_action)
        self.iface.removeToolBarIcon(self.action)

    # ==========================================
    # Main Execution
    # ==========================================
    def run(self):
        """Toggle the visibility of the floating protractor widget."""
        if self.widget is None:
            # Lazy import to speed up QGIS startup time
            from .protractor_widget import ProtractorWidget

            self.widget = ProtractorWidget(
                self.iface.mainWindow(),
                self.canvas
            )
            
            # Connect signal from widget to create line layer
            self.widget.request_line_creation.connect(self.create_line_layer)

        if self.widget.isVisible():
            self.widget.hide()
            self.action.setChecked(False)
        else:
            self.widget.show()
            self.action.setChecked(True)

    # ==========================================
    # Layer Processing
    # ==========================================
    def create_line_layer(self, azimuth):
        """
        Creates a temporary memory layer drawing a line from the 
        center of the protractor to the current cursor position.
        """
        if azimuth == -999.0:
            return

        canvas = self.canvas

        # Calculate Global to Map Coordinates for Center Point
        rect = self.widget.rect()
        center_global = self.widget.mapToGlobal(rect.center())
        p1 = canvas.getCoordinateTransform().toMapCoordinates(
            canvas.mapFromGlobal(center_global)
        )

        # Calculate Global to Map Coordinates for Cursor Point
        cursor_global = self.widget.mapToGlobal(self.widget.cursor_pos_local)
        p2 = canvas.getCoordinateTransform().toMapCoordinates(
            canvas.mapFromGlobal(cursor_global)
        )

        # Prepare Memory Vector Layer
        crs_id = canvas.mapSettings().destinationCrs().authid()
        layer_name = f"Sector_Azimuth_{azimuth:.1f}"

        vl = QgsVectorLayer(
            f"LineString?crs={crs_id}",
            layer_name,
            "memory"
        )
        provider = vl.dataProvider()

        # Set up Attributes (Azimuth Field)
        az_field = QgsField(
            "Azimuth",
            QVariant.Double,
            "double",
            10,
            2
        )
        provider.addAttributes([az_field])
        vl.updateFields()

        # Generate Line Geometry
        feature = QgsFeature()
        feature.setGeometry(
            QgsGeometry.fromPolylineXY([
                QgsPointXY(p1),
                QgsPointXY(p2)
            ])
        )
        feature.setAttributes([azimuth])
        provider.addFeatures([feature])

        # Apply Red Solid Line Styling
        line_symbol = QgsLineSymbol.createSimple({
            "color": "red",
            "width": "1.0",
            "line_style": "solid"
        })
        vl.setRenderer(QgsSingleSymbolRenderer(line_symbol))

        # Add to QGIS Project Canvas
        QgsProject.instance().addMapLayer(vl)
        vl.triggerRepaint()

    # ==========================================
    # Information & Support
    # ==========================================
    def show_about(self):
        """Displays the plugin information, developer details, and support links."""
        msg = QMessageBox(self.iface.mainWindow())
        msg.setWindowTitle("About Bearing Protractor")
        msg.setIcon(QMessageBox.Information)
        msg.setTextFormat(Qt.RichText)
        
        # HTML Styling for Global Audience + Bilingual Support
        text = (
            "<h3>Bearing Protractor</h3>"
            "<b>Version:</b> 3.9.0<br>"
            "<b>Author:</b> Jujun Junaedi<br><br>"
            
            "<b>☕ Support & Donate:</b><br>"
            "If this tool saves you hours of work, consider buying me a coffee!<br>"
            "• <b>Global:</b> Buy Me a Coffee (buymeacoffee.com/juneth)<br>"
            "• <b>Indonesia:</b> OVO / GoPay (081510027058)<br><br>"
            
            "<div style='background-color: #e8f4f8; padding: 10px; border-radius: 5px; text-align: center; color: #2d98da; border: 1px solid #bdc3c7;'>"
            "<b>💡 PRO TIP FOR SHARING 💡</b><br>"
            "<span style='font-size: 11px;'>"
            "To ensure your colleagues get the latest version without bugs, please share the <b>Official QGIS Plugin Link</b> or <b>GitHub Link</b> instead of raw ZIP files.<br><br>"
            "<i>Biar rekan kerjamu selalu dapat versi terbaru yang bebas error, yuk biasakan share link resmi QGIS/GitHub, bukan bagi-bagi file ZIP mentahan 😉</i>"
            "</span>"
            "</div><br>"
            
            "<hr>"
            "<p align='center' style='color: #636e72; font-size: 11px;'>"
            "<i>\"May this tool be a continuous charity (amal jariah),<br>especially for my beloved late parents. 🤲\"</i>"
            "</p>"
        )
        
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()