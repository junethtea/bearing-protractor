# Bearing Protractor for QGIS 📡

[![QGIS Plugin](https://img.shields.io/badge/QGIS-Plugin-588225.svg?style=flat-square)](https://plugins.qgis.org/plugins/)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-e6a304.svg?style=flat-square)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Donate](https://img.shields.io/badge/Donate-Buy%20Me%20a%20Coffee-ff813f.svg?style=flat-square)](https://buymeacoffee.com/juneth)

**Bearing Protractor** is an advanced, interactive floating planning tool designed specifically for QGIS (fully compatible with QGIS 3.x and QGIS 4.x). Built with Telecommunications Professionals, RF Engineers, and GIS Analysts in mind, it provides an on-screen, draggable protractor overlay to significantly speed up cell planning, neighbor optimization, physical tuning analysis, and site audits.

## 🌟 Key Features
* **Interactive Floating Widget:** A transparent, frameless protractor that sits above your map canvas without blocking your spatial data view.
* **Dynamic Multiple Sectors:** Create, drag, and adjust multiple sector antennas (needles) to accurately visualize coverage direction and beamwidth.
* **Real-Time Distance Tracking:** Automatically calculates and displays real-world distances (in Meters or Kilometers) dynamically, utilizing the map canvas CRS and transform context.
* **Cell Footprint Generation:** Export current sector configurations (azimuth and beamwidth) directly to the map canvas as physical polygon vector layers (`Cell_Footprint`) for advanced spatial analysis.
* **1-Click Tabular Export:** Instantly copy sector data (Sector Label, Azimuth, Beamwidth, Distance) to the clipboard for effortless reporting in Spreadsheet applications.
* **Manual Measurement Ruler:** Double-click the center to draw a temporary line to instantly check the exact azimuth and distance to neighbor sites.
* **Persistent Settings:** All visual customizations (ring size, colors, fonts, sector counts, crosshair styles) are automatically saved across QGIS sessions.
* **Bilingual Support:** Seamlessly switch the UI between English and Indonesian.

## 🎯 Target Audience
This plugin is highly recommended for:
* **RF Optimization Engineers** verifying physical tuning, drive test data, and antenna azimuths.
* **Cellular Network Planners** simulating macro-cell and micro-cell coverage footprints.
* **GIS Analysts** working with spatial telecommunication databases.

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
3. **Main Menu:** Right-Click on any empty space inside the ring to add sectors, export footprints, copy data, or change styles.
4. **Edit Sector:** Right-Click directly on the tip/arrow of a sector line (S1, S2, etc.) to change its color, label, or beamwidth.
5. **Adjust Sector Length:** Left-Click & Hold on a sector line, then drag away/towards the center.
6. **Manual Measurement Line:** Double-Click the center point (or use the right-click menu). Drag the cursor to the target, then Left-Click to lock. Press **ESC** to cancel.

## 📸 Screenshots

**1. Bearing Protractor Overview**

<img width="526" height="387" alt="Bearing" src="https://github.com/user-attachments/assets/c2fb2510-fef3-4542-8967-917578079a17" />

**2. Menu Settings**

<img width="525" height="387" alt="Menu Seting" src="https://github.com/user-attachments/assets/10039ba5-8ba9-43cd-a09c-5a42f82a8680" />

**3. Bearing Settings**

<img width="526" height="385" alt="Bearing Menu" src="https://github.com/user-attachments/assets/f2efa3f4-f04e-4236-b674-9e141a61b431" />

**4. Visual Setting**

<img width="526" height="388" alt="Visual Setting" src="https://github.com/user-attachments/assets/46c5cf7f-6405-4f38-bae9-b32af8a99562" />

**5. Manual Measurement Ruler**

<img width="526" height="388" alt="Manual ruler" src="https://github.com/user-attachments/assets/5417b8cd-e074-4c1f-9da4-3549b765ccf0" />

**6. New Style**

<img width="542" height="389" alt="New" src="https://github.com/user-attachments/assets/fd32ef3c-8b65-4cdf-9d3e-27abd696c6a3" />

<img width="1508" height="1080" alt="New Style" src="https://github.com/user-attachments/assets/467c2c8e-d6bb-4d92-aecd-feb587bc963e" />

**7. Added QGIS 4.x (PyQt6) compatibility support**
<img width="582" height="259" alt="QGIS 4 0" src="https://github.com/user-attachments/assets/f8eeb2bf-7c60-42a3-95bc-4a511e55fbbc" />

**8. New feature Export Footprint & Copy Data**
<img width="602" height="388" alt="New Feature" src="https://github.com/user-attachments/assets/a8677f57-608d-4d1b-990b-90ad3a1a41eb" />

<img width="603" height="388" alt="Export" src="https://github.com/user-attachments/assets/1e06a7d4-aa75-4404-94aa-5454d328c710" />
<img width="604" height="389" alt="Copy Data" src="https://github.com/user-attachments/assets/c19ee9bd-8b17-474d-858d-48a3441eb740" />

<img width="603" height="388" alt="Result Export" src="https://github.com/user-attachments/assets/6d6d6aab-e113-4a42-9ca9-68b39fbe9b55" />
<img width="225" height="144" alt="Result Copy" src="https://github.com/user-attachments/assets/f21af3af-d03c-4274-b398-e2d8a15f5a72" />


## ☕ Support the Developer
If this tool saves you hours of work, consider buying me a coffee to support future development! 
* 🌍 **Global:** [Buy Me a Coffee](https://buymeacoffee.com/juneth)
* 🇮🇩 **Indonesia:** OVO / GoPay (`081510027058`)

*"May this tool be a continuous charity (amal jariah), especially for my beloved late parents. 🤲"*

## 👨‍💻 About the Author
Hi! I'm **Jujun Junaedi (Jun)**, a Telecommunications & NPO Engineer who loves simplifying complex workflows. I build open-source QGIS plugins (like *Bearing Protractor*, *Embed Legend*, and *Site Sector*) to help RF and Network Planning engineers work faster and smarter. 

With years of hands-on experience in field optimization and spatial data analysis, my goal is to create practical, everyday tools that bridge the gap between telecommunications and GIS.

Let's connect:
* 📧 **Email:** jujun.junaedi@outlook.com
* 📱 **Phone / WhatsApp:** +62 815-1002-7058
* 💼 **LinkedIn:** [Jujun Junaedi](https://www.linkedin.com/in/jujun-j-2873a9254)

## 📄 License
This project is licensed under the GNU General Public License v2.0 or later (GPL-2.0-or-later). See the [LICENSE](LICENSE) file for details.
