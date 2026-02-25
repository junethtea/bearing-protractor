# Bearing Protractor for QGIS 📡

[![QGIS Plugin](https://img.shields.io/badge/QGIS-Plugin-588225.svg?style=flat-square)](https://plugins.qgis.org/plugins/)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-e6a304.svg?style=flat-square)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Donate](https://img.shields.io/badge/Donate-Buy%20Me%20a%20Coffee-ff813f.svg?style=flat-square)](https://buymeacoffee.com/juneth)

**Bearing Protractor** is an advanced, interactive floating planning tool designed specifically for QGIS. Built with Telecommunications Professionals, RF Engineers, and GIS Analysts in mind, it provides an on-screen, draggable protractor overlay to speed up cell planning, neighbor optimization, and site audits.

## 🌟 Key Features
* **Interactive Floating Widget:** A transparent, frameless protractor that sits above your map canvas without blocking your view.
* **Dynamic Multiple Sectors:** Create, drag, and adjust multiple sector antennas (needles) to visualize coverage direction and beamwidth.
* **Real-Time Distance Tracking:** Automatically calculates and displays real-world distances (in Meters or Kilometers) dynamically, based on your map's scale and CRS.
* **Manual Measurement Ruler:** Double-click the center to draw a temporary line to instantly check the azimuth and distance to neighbor sites.
* **Persistent Settings:** All visual customizations (ring size, colors, fonts, sector counts) are automatically saved across QGIS sessions.
* **Bilingual Support:** Seamlessly switch the UI between English and Indonesian.

## 🎯 Target Audience
This plugin is highly recommended for:
* **RF Optimization Engineers** checking physical tuning and antenna azimuths.
* **Cellular Network Planners** simulating macro-cell and micro-cell coverage.
* **GIS Analysts** working with spatial telecommunication data.

## 🛠️ Installation
### Via QGIS Plugin Repository (Recommended)
1. Open QGIS.
2. Go to **Plugins** -> **Manage and Install Plugins...**
3. Search for **Bearing Protractor**.
4. Click **Install Plugin**.

### Manual Installation (ZIP)
1. Download the latest `.zip` release from this repository.
2. Open QGIS, go to **Plugins** -> **Manage and Install Plugins...** -> **Install from ZIP**.
3. Select the downloaded `.zip` file and click **Install**.

## 📖 How to Use
1. **Move Protractor:** Left-Click & Hold on the ring area, then drag the mouse.
2. **Resize Ring:** Hover over the ring and use the *Mouse Scroll Wheel*.
3. **Main Menu:** Right-Click on any empty space inside the ring to add sectors or change settings.
4. **Edit Sector:** Right-Click directly on the tip/arrow of a sector line (S1, S2, etc.) to change its color, label, or beamwidth.
5. **Adjust Sector Length:** Left-Click & Hold on a sector line, then drag away/towards the center.
6. **Manual Measurement Line:** Double-Click the center point (or use the right-click menu). Drag the cursor to the target, then Left-Click to lock. Press **ESC** to cancel.

## 📸 Screenshots

**1.Bearing Protractor Overview**

<img width="526" height="387" alt="Bearing" src="https://github.com/user-attachments/assets/c2fb2510-fef3-4542-8967-917578079a17" />

**2.Menu Settings**

<img width="525" height="387" alt="Menu Seting" src="https://github.com/user-attachments/assets/10039ba5-8ba9-43cd-a09c-5a42f82a8680" />

**3.Bearing Settings**

<img width="526" height="385" alt="Bearing Menu" src="https://github.com/user-attachments/assets/f2efa3f4-f04e-4236-b674-9e141a61b431" />

**4.Visual Setting**

<img width="526" height="388" alt="Visual Setting" src="https://github.com/user-attachments/assets/46c5cf7f-6405-4f38-bae9-b32af8a99562" />

**5.Manual Measurement Ruler**

<img width="526" height="388" alt="Manual ruler" src="https://github.com/user-attachments/assets/5417b8cd-e074-4c1f-9da4-3549b765ccf0" />

## ☕ Support the Developer
If this tool saves you hours of work, consider buying me a coffee to support future development! 
* 🌍 **Global:** [Buy Me a Coffee](https://buymeacoffee.com/juneth)
* 🇮🇩 **Indonesia:** OVO / GoPay (`081510027058`)

*"May this tool be a continuous charity (amal jariah), especially for my beloved late parents. 🤲"*

## 📄 License
This project is licensed under the GNU General Public License v2.0 or later (GPL-2.0-or-later). See the [LICENSE](LICENSE) file for details.
