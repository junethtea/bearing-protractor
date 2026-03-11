#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------_-----------------
#  Bearing Protractor - QGIS Floating Planning Tool
# --------------------------------------------------------------------------
#  PLUGIN NAME : Bearing Protractor
#  DESCRIPTION : Floating interactive protractor for RF planning & audit, Features real-time distance tracking & multi-sector support.
#  AUTHOR      : Jujun Junaedi
#  EMAIL       : jujun.junaedi@outlook.com
#  VERSION     : 3.9.2
#  COPYRIGHT   : (c) 2024 by Jujun Junaedi
#  LICENSE     : GPL-2.0-or-later
#  MOTTO       : "Sebaik-baiknya Manusia adalah yang bermanfaat bagi sesama"
# --------------------------------------------------------------------------

"""
LICENSE AGREEMENT:
This program is free software; you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software Foundation.
To support the developer and ensure you have the latest stable version, 
please download directly from the Official QGIS Repository.
"""

import os
import math
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QVariant, Qt, QPoint

# PyQt5 / PyQt6 Compatibility Handling
try:
    from qgis.PyQt.QtGui import QAction
except ImportError:
    from qgis.PyQt.QtWidgets import QAction

MsgBox_Info = QMessageBox.Icon.Information if hasattr(QMessageBox, 'Icon') else QMessageBox.Information
MsgBox_Ok = QMessageBox.StandardButton.Ok if hasattr(QMessageBox, 'StandardButton') else QMessageBox.Ok
Qt_RichText = Qt.TextFormat.RichText if hasattr(Qt, 'TextFormat') else Qt.RichText

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsField,
    QgsSingleSymbolRenderer,
    QgsLineSymbol,
    QgsFillSymbol
)

class BearingProtractorPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.plugin_dir = os.path.dirname(__file__)

        self.widget = None
        self.action = None
        self.about_action = None

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()

        self.action = QAction(icon, "Bearing Protractor", self.iface.mainWindow())
        self.action.setCheckable(True)
        self.action.triggered.connect(self.run)

        self.about_action = QAction("About Bearing Protractor", self.iface.mainWindow())
        self.about_action.triggered.connect(self.show_about)

        self.iface.addPluginToMenu("&Bearing Protractor", self.action)
        self.iface.addPluginToMenu("&Bearing Protractor", self.about_action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.widget:
            self.widget.close()

        self.iface.removePluginMenu("&Bearing Protractor", self.action)
        self.iface.removePluginMenu("&Bearing Protractor", self.about_action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        if self.widget is None:
            from .protractor_widget import ProtractorWidget

            self.widget = ProtractorWidget(
                self.iface.mainWindow(),
                self.canvas
            )
            self.widget.request_line_creation.connect(self.create_line_layer)
            self.widget.request_footprint_creation.connect(self.create_footprint_layer)

        if self.widget.isVisible():
            self.widget.hide()
            self.action.setChecked(False)
        else:
            self.widget.show()
            self.action.setChecked(True)

    def create_line_layer(self, azimuth):
        if azimuth == -999.0:
            return

        canvas = self.canvas
        rect = self.widget.rect()
        center_global = self.widget.mapToGlobal(rect.center())
        p1 = canvas.getCoordinateTransform().toMapCoordinates(
            canvas.mapFromGlobal(center_global)
        )

        cursor_global = self.widget.mapToGlobal(self.widget.cursor_pos_local)
        p2 = canvas.getCoordinateTransform().toMapCoordinates(
            canvas.mapFromGlobal(cursor_global)
        )

        crs_id = canvas.mapSettings().destinationCrs().authid()
        layer_name = f"Sector_Azimuth_{azimuth:.1f}"

        vl = QgsVectorLayer(f"LineString?crs={crs_id}", layer_name, "memory")
        provider = vl.dataProvider()

        az_field = QgsField("Azimuth", QVariant.Double, "double", 10, 2)
        provider.addAttributes([az_field])
        vl.updateFields()

        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolylineXY([QgsPointXY(p1), QgsPointXY(p2)]))
        feature.setAttributes([azimuth])
        provider.addFeatures([feature])

        line_symbol = QgsLineSymbol.createSimple({
            "color": "red",
            "width": "1.0",
            "line_style": "solid"
        })
        vl.setRenderer(QgsSingleSymbolRenderer(line_symbol))

        QgsProject.instance().addMapLayer(vl)
        vl.triggerRepaint()

    def create_footprint_layer(self, arms, center_local):
        if not arms:
            return
        
        canvas = self.canvas
        crs_id = canvas.mapSettings().destinationCrs().authid()
        vl = QgsVectorLayer(f"Polygon?crs={crs_id}", "Cell_Footprint", "memory")
        provider = vl.dataProvider()
        
        fields = [
            QgsField("Sector", QVariant.String, "string", 50),
            QgsField("Azimuth", QVariant.Double, "double", 10, 2),
            QgsField("Beamwidth", QVariant.Double, "double", 10, 2)
        ]
        provider.addAttributes(fields)
        vl.updateFields()
        
        features = []
        
        # Helper for coordinate transformation
        def local_to_map(px, py):
            global_pt = self.widget.mapToGlobal(QPoint(int(px), int(py)))
            canvas_pt = canvas.mapFromGlobal(global_pt)
            return canvas.getCoordinateTransform().toMapCoordinates(canvas_pt)
        
        center_map = local_to_map(center_local.x(), center_local.y())
        
        for arm in arms:
            angle = arm["angle"]
            bw = arm.get("beamwidth", 45)
            ratio = arm.get("ratio", 1.15)
            radius_px = self.widget.ring_radius * ratio
            
            if bw <= 0:
                continue
                
            start_angle = angle - bw / 2
            end_angle = angle + bw / 2
            
            poly_points = [center_map]
            
            # Create smooth curve with 5-degree steps
            step = 5
            curr_angle = start_angle
            while curr_angle <= end_angle:
                rad = math.radians(curr_angle - 90)
                px = center_local.x() + radius_px * math.cos(rad)
                py = center_local.y() + radius_px * math.sin(rad)
                poly_points.append(local_to_map(px, py))
                curr_angle += step
                
            # Ensure exact end angle is included
            if curr_angle - step < end_angle:
                rad = math.radians(end_angle - 90)
                px = center_local.x() + radius_px * math.cos(rad)
                py = center_local.y() + radius_px * math.sin(rad)
                poly_points.append(local_to_map(px, py))
                
            poly_points.append(center_map)
            
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPolygonXY([poly_points]))
            feat.setAttributes([arm.get("label", ""), angle, bw])
            features.append(feat)
            
        provider.addFeatures(features)
        
        # Transparent styling
        symbol = QgsFillSymbol.createSimple({
            "color": "0,255,255,80",
            "outline_color": "0,255,255,255",
            "outline_width": "0.5"
        })
        vl.setRenderer(QgsSingleSymbolRenderer(symbol))
        
        QgsProject.instance().addMapLayer(vl)
        vl.triggerRepaint()

    def show_about(self):
        msg = QMessageBox(self.iface.mainWindow())
        msg.setWindowTitle("About Bearing Protractor")
        msg.setIcon(MsgBox_Info)
        msg.setTextFormat(Qt_RichText)
        
        text = (
            "<h3>Bearing Protractor</h3>"
            "<b>Version:</b> 3.9.2<br>"
            "<b>Author:</b> Jujun Junaedi<br><br>"
            "<b>☕ Support & Donate:</b><br>"
            "If this tool saves you hours of work, consider buying me a coffee!<br><br>"
            
            "<table width='100%'><tr><td align='center'>"
            "<table cellpadding='5' cellspacing='0' border='0'>"
            "<tr>"
            "<td valign='middle'><b><font size='7'>Click 👉</font></b></td>"
            "<td valign='middle'>"
            "<a href='https://buymeacoffee.com/juneth' style='text-decoration: none;'>"
            "<table bgcolor='#FFDD00' cellpadding='10' cellspacing='0' border='0' style='border-radius: 5px; border: 1px solid #000000;'>"
            "<tr>"
            "<td align='center' style='color: black; font-weight: bold; font-family: sans-serif; font-size: 14px;'>"
            "&nbsp;☕ Buy me a coffee!&nbsp;"
            "</td>"
            "</tr>"
            "</table>"
            "</a>"
            "</td>"
            "</tr>"
            "</table>"
            "</td></tr></table><br>"
            
            "Yuk bisa yuk apresiasinya! 👇<br><br>"
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
        msg.setStandardButtons(MsgBox_Ok)
        if hasattr(msg, 'exec'):
            msg.exec()
        else:
            msg.exec_()