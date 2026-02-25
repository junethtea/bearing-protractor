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
LICENSE AGREEMENT:
This program is free software; you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software Foundation.
To support the developer and ensure you have the latest stable version, 
please download directly from the Official QGIS Repository.
"""

import math
import json
from qgis.core import QgsSettings, QgsDistanceArea, QgsProject
from qgis.PyQt.QtCore import Qt, QPoint, QPointF, QRectF, pyqtSignal
from qgis.PyQt.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, 
    QPolygonF, QPainterPath
)
from qgis.PyQt.QtWidgets import (
    QWidget, QMenu, QColorDialog, QInputDialog, 
    QMessageBox, QAction
)

class ProtractorWidget(QWidget):
    """
    Main Widget Class for Bearing Protractor.
    Handles painting, mouse events, and context menus.
    """
    
    # Signal to communicate with the main plugin file
    request_line_creation = pyqtSignal(float)

    def __init__(self, parent=None, canvas=None):
        super().__init__(parent)
        self.canvas = canvas
        self.settings = QgsSettings()
        
        # --- GIS Calculation Tools ---
        self.da = QgsDistanceArea()
        self.da.setEllipsoid(QgsProject.instance().ellipsoid())
        self.da.setSourceCrs(
            QgsProject.instance().crs(), 
            QgsProject.instance().transformContext()
        )

        # --- Window Configuration ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.resize(1000, 1000)

        # --- Localization ---
        self.current_lang = "ID"
        self.texts = {
            "ID": {
                "menu_bearing": "Bearing", "show_all": "Tampilkan Semua", 
                "show_labels": "Tampilkan Label", "show_beam": "Tampilkan Beamwidth", 
                "add_new": "Tambah Bearing", "reset": "Reset Semua",
                "set_count": "Atur Jumlah Bearing", "manual_line": "Tarik Garis Manual",
                "style_menu": "Visual Settings", "thick_ring": "Tebal Ring", 
                "size_font": "Ukuran Angka", "color_ring": "Warna Ring", 
                "color_text": "Warna Teks", "lang_menu": "Bahasa / Language", 
                "help_menu": "Cara Penggunaan / Help",
                "about_menu": "Tentang Plugin / About", "edit_header": "Edit Bearing: ", 
                "change_color": "Ganti Warna", "change_label": "Ganti Nama / Label",
                "change_beam": "Atur Lebar Beam", "delete_bearing": "Hapus Bearing"
            },
            "EN": {
                "menu_bearing": "Bearings", "show_all": "Show All", 
                "show_labels": "Show Labels", "show_beam": "Show Beamwidth", 
                "add_new": "Add New", "reset": "Reset All",
                "set_count": "Set Count", "manual_line": "Draw Manual Line",
                "style_menu": "Visual Settings", "thick_ring": "Ring Weight", 
                "size_font": "Font Size", "color_ring": "Ring Color", 
                "color_text": "Text Color", "lang_menu": "Language", 
                "help_menu": "How to Use / Help",
                "about_menu": "About Plugin", "edit_header": "Edit Bearing: ", 
                "change_color": "Change Color", "change_label": "Change Label",
                "change_beam": "Set Beamwidth", "delete_bearing": "Delete Bearing"
            }
        }

        # --- Internal State ---
        self.arms = []
        self.show_arms = True
        self.show_bearing_labels = True
        self.show_beamwidth = True
        
        self.is_dragging_window = False
        self.is_hovering_center = False
        self.is_dragging_arm = False
        self.is_picking_azimuth = False
        
        self.drag_offset = QPoint(0, 0)
        self.cursor_pos_local = QPoint(0, 0)
        self.current_cursor_azimuth = 0.0
        self.active_arm_index = -1

        self.load_settings()

    def t(self, key):
        return self.texts[self.current_lang].get(key, key)

    def get_real_distance(self, p1_local, p2_local):
        if not self.canvas:
            return "0m"
        try:
            transform = self.canvas.getCoordinateTransform()
            p1_global = self.mapToGlobal(p1_local)
            p2_global = self.mapToGlobal(p2_local)
            p1_canvas = self.canvas.mapFromGlobal(p1_global)
            p2_canvas = self.canvas.mapFromGlobal(p2_global)
            p1_map = transform.toMapCoordinates(p1_canvas.x(), p1_canvas.y())
            p2_map = transform.toMapCoordinates(p2_canvas.x(), p2_canvas.y())
            
            dist = self.da.measureLine(p1_map, p2_map)
            if dist >= 1000:
                return f"{dist/1000:.2f}km"
            return f"{int(dist)}m"
        except Exception:
            return "0m"

    # ==========================================
    # Settings Management
    # ==========================================
    def load_settings(self):
        s = self.settings
        self.ring_radius = int(s.value("BearingProtractor/ring_radius", 150))
        self.ring_thickness = int(s.value("BearingProtractor/ring_thickness", 2))
        self.font_size = int(s.value("BearingProtractor/font_size", 7))
        self.ring_color = QColor(s.value("BearingProtractor/ring_color", "yellow"))
        self.text_color = QColor(s.value("BearingProtractor/text_color", "yellow"))
        self.text_stroke_color = QColor("black")
        self.bearing_thickness = 3
        try:
            raw = json.loads(s.value("BearingProtractor/arms_data", "[]"))
            self.arms = [dict(a, color=QColor(a['color'])) for a in raw]
        except:
            self.arms = []

    def save_settings(self):
        s = self.settings
        s.setValue("BearingProtractor/ring_radius", self.ring_radius)
        s.setValue("BearingProtractor/ring_thickness", self.ring_thickness)
        s.setValue("BearingProtractor/font_size", self.font_size)
        s.setValue("BearingProtractor/ring_color", self.ring_color.name())
        s.setValue("BearingProtractor/text_color", self.text_color.name())
        temp = [dict(a, color=a['color'].name()) for a in self.arms]
        s.setValue("BearingProtractor/arms_data", json.dumps(temp))

    # ==========================================
    # Input Events
    # ==========================================
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.is_picking_azimuth:
            self.stop_manual_picking()
        super().keyPressEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.ring_radius = min(450, self.ring_radius + 10)
        else:
            self.ring_radius = max(50, self.ring_radius - 10)
        self.save_settings()
        self.update()
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_picking_azimuth:
                self.request_line_creation.emit(self.current_cursor_azimuth)
                self.stop_manual_picking()
            else:
                center = self.rect().center()
                dist = math.sqrt((event.pos().x()-center.x())**2 + (event.pos().y()-center.y())**2)
                
                if abs(dist - self.ring_radius) < 15:
                    self.start_manual_picking()
                elif dist < 45:
                    self.is_dragging_window = True
                    self.drag_offset = event.globalPos() - self.pos()
                else:
                    idx = self.get_clicked_arm(event.pos())
                    if idx != -1:
                        self.active_arm_index = idx
                        self.is_dragging_arm = True
                    else:
                        self.is_dragging_window = True
                        self.drag_offset = event.globalPos() - self.pos()
        self.update()

    def mouseMoveEvent(self, event):
        center = self.rect().center()
        dx = event.pos().x() - center.x()
        dy = event.pos().y() - center.y()
        
        self.cursor_pos_local = event.pos()
        self.current_cursor_azimuth = (math.degrees(math.atan2(dx, -dy)) + 360) % 360
        
        if self.is_dragging_arm:
            self.arms[self.active_arm_index]['angle'] = self.current_cursor_azimuth
            current_dist = math.sqrt(dx**2 + dy**2)
            self.arms[self.active_arm_index]['ratio'] = max(1.0, current_dist / self.ring_radius)
            
        elif self.is_dragging_window:
            self.move(event.globalPos() - self.drag_offset)
            
        self.is_hovering_center = math.sqrt(dx**2 + dy**2) < 45
        self.update()

    def mouseReleaseEvent(self, event):
        if self.is_dragging_arm:
            self.save_settings()
        self.is_dragging_window = False
        self.is_dragging_arm = False
        
        if event.button() == Qt.RightButton:
            idx = self.get_clicked_arm(event.pos())
            if idx != -1:
                self.show_arm_context_menu(event.pos(), idx)
            else:
                self.show_main_context_menu(event.pos())

    def mouseDoubleClickEvent(self, event):
        self.start_manual_picking()

    # ==========================================
    # Painting / Drawing
    # ==========================================
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        center = self.rect().center()
        radius = self.ring_radius
        
        if self.show_arms:
            for arm in self.arms:
                self.draw_arm_with_beam(p, center, radius, arm)
        
        if self.is_hovering_center:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, 80))
            p.drawEllipse(center, 25, 25)
        
        p.setPen(QPen(QColor("yellow"), 2))
        p.drawLine(center.x()-15, center.y(), center.x()+15, center.y())
        p.drawLine(center.x(), center.y()-15, center.x(), center.y()+15)
        
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(self.ring_color, self.ring_thickness))
        p.drawEllipse(center, radius, radius)
        
        for deg in range(0, 360, 2):
            rad = math.radians(deg - 90)
            t_len = 10 if deg % 10 == 0 else 5
            p.setPen(QPen(QColor("red") if deg == 0 else self.ring_color, self.ring_thickness if deg % 10 == 0 else 1))
            p1 = QPointF(center.x() + radius * math.cos(rad), center.y() + radius * math.sin(rad))
            p2 = QPointF(center.x() + (radius - t_len) * math.cos(rad), center.y() + (radius - t_len) * math.sin(rad))
            p.drawLine(p1, p2)
            if deg % 10 == 0:
                self.draw_curved_text(p, str(deg), center, radius - 18, deg)
        
        if self.is_picking_azimuth:
            self.draw_preview_line(p, center)
            
        p.end()

    def draw_curved_text(self, p, text, center, distance, angle):
        p.save()
        p.translate(center)
        p.rotate(angle)
        font = QFont("Arial", self.font_size, QFont.Bold)
        p.setFont(font)
        tw = p.fontMetrics().width(text)
        path = QPainterPath()
        path.addText(-tw/2, -distance, font, text)
        p.setPen(QPen(self.text_stroke_color, 2))
        p.drawPath(path)
        p.setPen(Qt.NoPen)
        p.setBrush(self.text_color)
        p.drawPath(path)
        p.restore()

    def draw_arm_with_beam(self, p, center, radius, arm):
        angle = arm["angle"]
        color = arm["color"]
        bw = arm.get("beamwidth", 45)
        ratio = arm.get("ratio", 1.15)
        rad = math.radians(angle - 90)
        arm_len = radius * ratio
        tip = QPointF(center.x() + arm_len * math.cos(rad), center.y() + arm_len * math.sin(rad))
        dist_str = self.get_real_distance(center, tip.toPoint())
        
        if bw > 0 and self.show_beamwidth:
            bc = QColor(color)
            bc.setAlpha(60)
            p.setBrush(bc)
            p.setPen(Qt.NoPen)
            p.drawPie(QRectF(center.x()-arm_len, center.y()-arm_len, arm_len*2, arm_len*2), int((90-angle+bw/2)*16), int(-bw*16))
        
        p.setPen(QPen(color, self.bearing_thickness))
        p.drawLine(center, tip)
        
        arrow = QPolygonF([
            tip,
            QPointF(tip.x() + 12 * math.cos(rad + math.radians(150)), tip.y() + 12 * math.sin(rad + math.radians(150))),
            QPointF(tip.x() + 12 * math.cos(rad - math.radians(150)), tip.y() + 12 * math.sin(rad - math.radians(150)))
        ])
        p.setBrush(QBrush(color))
        p.drawPolygon(arrow)
        
        if self.show_bearing_labels:
            offset_x = tip.x() + 35 * math.cos(rad)
            offset_y = tip.y() + 35 * math.sin(rad)
            self.draw_outlined_text(p, f"{arm['label']} ({dist_str})", offset_x, offset_y, color)

    def draw_outlined_text(self, p, text, x, y, text_color):
        font = QFont("Arial", self.font_size, QFont.Bold)
        p.setFont(font)
        tw = p.fontMetrics().width(text)
        path = QPainterPath()
        path.addText(x - tw/2, y, font, text)
        p.setPen(QPen(self.text_stroke_color, 3))
        p.drawPath(path)
        p.setPen(Qt.NoPen)
        p.setBrush(text_color)
        p.drawPath(path)

    def draw_preview_line(self, p, center):
        dist_str = self.get_real_distance(center, self.cursor_pos_local)
        p.setPen(QPen(QColor("red"), 2, Qt.DashLine))
        p.drawLine(center, self.cursor_pos_local)
        
        dx = self.cursor_pos_local.x() - center.x()
        dy = self.cursor_pos_local.y() - center.y()
        ang_rad = math.atan2(dy, dx)
        
        tx = self.cursor_pos_local.x() + 15 * math.cos(ang_rad)
        ty = self.cursor_pos_local.y() + 15 * math.sin(ang_rad)
        self.draw_outlined_text(p, f"{self.current_cursor_azimuth:.1f}° | {dist_str}", tx, ty, QColor("red"))

    # ==========================================
    # Menus & Actions
    # ==========================================
    def show_main_context_menu(self, pos):
        menu = QMenu(self)
        
        m_b = menu.addMenu(self.t('menu_bearing'))
        m_b.addAction(QAction(self.t('show_all'), self, checkable=True, checked=self.show_arms, triggered=lambda: setattr(self, 'show_arms', not self.show_arms)))
        m_b.addAction(QAction(self.t('show_labels'), self, checkable=True, checked=self.show_bearing_labels, triggered=lambda: setattr(self, 'show_bearing_labels', not self.show_bearing_labels)))
        m_b.addAction(QAction(self.t('show_beam'), self, checkable=True, checked=self.show_beamwidth, triggered=lambda: setattr(self, 'show_beamwidth', not self.show_beamwidth)))
        m_b.addSeparator()
        m_b.addAction(self.t('add_new'), self.add_new_arm)
        m_b.addAction(self.t('set_count'), self.ask_for_arm_count)
        m_b.addAction(self.t('reset'), self.reset_arms)

        menu.addAction(self.t('manual_line'), self.start_manual_picking)
        
        m_s = menu.addMenu(self.t('style_menu'))
        m_s.addAction(self.t('size_font'), lambda: self.set_visual_value("font_s"))
        m_s.addAction(self.t('thick_ring'), lambda: self.set_visual_value("ring_t"))
        m_s.addSeparator()
        m_s.addAction(self.t('color_ring'), lambda: self.pick_color('ring_color'))
        m_s.addAction(self.t('color_text'), lambda: self.pick_color('text_color'))
        
        m_l = menu.addMenu(self.t('lang_menu'))
        m_l.addAction("Indonesian", lambda: setattr(self, 'current_lang', 'ID'))
        m_l.addAction("English", lambda: setattr(self, 'current_lang', 'EN'))
        
        menu.addSeparator()
        menu.addAction(self.t('help_menu'), self.show_help_dialog)
        menu.addAction(self.t('about_menu'), self.show_about_dialog)
        
        menu.exec_(self.mapToGlobal(pos))

    def show_arm_context_menu(self, pos, idx):
        menu = QMenu(self)
        arm = self.arms[idx]
        menu.addSection(f"{self.t('edit_header')}{arm['label']}")
        menu.addAction(self.t('change_label'), lambda: self.edit_arm_label(idx))
        menu.addAction(self.t('change_color'), lambda: self.pick_arm_color(idx))
        menu.addAction(self.t('change_beam'), lambda: self.set_arm_beamwidth(idx))
        menu.addSeparator()
        menu.addAction(self.t('delete_bearing'), lambda: self.delete_arm(idx))
        menu.exec_(self.mapToGlobal(pos))

    def start_manual_picking(self):
        self.is_picking_azimuth = True
        self.setCursor(Qt.CrossCursor)
        self.grabMouse()
        self.update()

    def stop_manual_picking(self):
        self.is_picking_azimuth = False
        self.releaseMouse()
        self.unsetCursor()
        self.update()
    
    def get_clicked_arm(self, pos):
        center = self.rect().center()
        dx = pos.x() - center.x()
        dy = pos.y() - center.y()
        mouse_angle = (math.degrees(math.atan2(dx, -dy)) + 360) % 360
        for i, arm in enumerate(self.arms):
            if abs(arm['angle'] - mouse_angle) < 10:
                return i
        return -1

    def add_new_arm(self):
        self.arms.append({'angle': 0.0, 'color': QColor("cyan"), 'label': f"S{len(self.arms)+1}", 'beamwidth': 45, 'ratio': 1.15})
        self.save_settings()
        self.update()

    def ask_for_arm_count(self):
        count, ok = QInputDialog.getInt(self, self.t('set_count'), "Count:", len(self.arms), 1, 100)
        if ok:
            self.arms = [{'angle': (360/count) * i, 'color': QColor("cyan"), 'label': f"S{i+1}", 'beamwidth': 45, 'ratio': 1.15} for i in range(count)]
            self.save_settings()
            self.update()

    def reset_arms(self):
        self.arms = []
        self.save_settings()
        self.update()

    def delete_arm(self, idx):
        self.arms.pop(idx)
        self.save_settings()
        self.update()

    def edit_arm_label(self, idx):
        text, ok = QInputDialog.getText(self, self.t('change_label'), "Label:", text=self.arms[idx]['label'])
        if ok:
            self.arms[idx].update({'label': text})
            self.save_settings()
            self.update()

    def pick_arm_color(self, idx):
        color = QColorDialog.getColor(self.arms[idx]['color'], self)
        if color.isValid():
            self.arms[idx].update({'color': color})
            self.save_settings()
            self.update()

    def set_arm_beamwidth(self, idx):
        val, ok = QInputDialog.getInt(self, self.t('change_beam'), "BW:", self.arms[idx].get('beamwidth', 45), 0, 360)
        if ok:
            self.arms[idx].update({'beamwidth': val})
            self.save_settings()
            self.update()

    def pick_color(self, attr):
        current_color = getattr(self, attr)
        color = QColorDialog.getColor(current_color, self)
        if color.isValid():
            setattr(self, attr, color)
            self.save_settings()
            self.update()
    
    def set_visual_value(self, target):
        mapping = {"ring_t": 'ring_thickness', "font_s": 'font_size'}
        val, ok = QInputDialog.getInt(self, "Setting", "Value:", getattr(self, mapping[target]), 1, 100)
        if ok:
            setattr(self, mapping[target], val)
            self.save_settings()
            self.update()

    # ==========================================
    # Information Dialogs
    # ==========================================
    def show_help_dialog(self):
        """Displays a quick instruction guide for the users based on selected language."""
        msg = QMessageBox(self)
        msg.setWindowTitle(self.t("help_menu"))
        msg.setIcon(QMessageBox.Information)
        msg.setTextFormat(Qt.RichText)
        
        # Pengecekan Bahasa Dinamis
        if self.current_lang == "ID":
            text = (
                "<h3>Panduan Singkat</h3>"
                "<ul style='line-height: 1.5;'>"
                "<li><b>Pindah Posisi:</b> Klik Kiri & Tahan di area ring, lalu geser mouse.</li>"
                "<li><b>Ubah Ukuran (Resize):</b> Arahkan kursor ke ring, lalu gunakan <i>Scroll Mouse</i> (Roda Mouse).</li>"
                "<li><b>Menu Utama:</b> Klik Kanan di area kosong ring.</li>"
                "<li><b>Edit Sektor:</b> Klik Kanan tepat di garis ujung sektor (S1, S2, dst).</li>"
                "<li><b>Tarik Sektor Jauh/Dekat:</b> Klik Kiri & Tahan di garis sektor, lalu tarik menjauh/mendekat dari titik tengah.</li>"
                "<li><b>Garis Ukur Manual:</b> Klik 2x di titik tengah (atau via klik kanan). Tarik kursor ke target, lalu Klik Kiri untuk kunci garis. Tekan <b>ESC</b> untuk batal.</li>"
                "</ul>"
                "<hr>"
                "<p style='font-size: 11px; color: #555;'><i>Tip: Semua pengaturan warna, teks, dan ukuran akan tersimpan otomatis saat QGIS ditutup.</i></p>"
            )
        else:
            text = (
                "<h3>How to Use</h3>"
                "<ul style='line-height: 1.5;'>"
                "<li><b>Move Protractor:</b> Left-Click & Hold on the ring area, then drag the mouse.</li>"
                "<li><b>Resize Ring:</b> Hover over the ring and use the <i>Mouse Scroll Wheel</i>.</li>"
                "<li><b>Main Menu:</b> Right-Click on any empty space inside the ring.</li>"
                "<li><b>Edit Sector:</b> Right-Click directly on the tip/arrow of a sector line (S1, S2, etc.).</li>"
                "<li><b>Adjust Sector Length:</b> Left-Click & Hold on a sector line, then drag away/towards the center.</li>"
                "<li><b>Manual Measurement Line:</b> Double-Click the center point (or use the right-click menu). Drag the cursor to the target, then Left-Click to lock. Press <b>ESC</b> to cancel.</li>"
                "</ul>"
                "<hr>"
                "<p style='font-size: 11px; color: #555;'><i>Tip: All color, text, and size settings are automatically saved when QGIS is closed.</i></p>"
            )
        
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_about_dialog(self):
        """Displays the plugin information and support links."""
        msg = QMessageBox(self)
        msg.setWindowTitle(self.t("about_menu"))
        msg.setIcon(QMessageBox.Information)
        msg.setTextFormat(Qt.RichText)
        
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