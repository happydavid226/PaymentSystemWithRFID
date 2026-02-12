http://157.173.101.159:9216/
# 💳 RFID Smart Wallet System
**Team ID:** ubuliza_david  
**Hardware:** ESP8266 + MFRC522 RFID Reader  
**Backend:** Node.js + MQTT + WebSockets

A real-time RFID balance management system that allows physical cards to be used as digital wallets. The system features physical writing to RFID sectors and a live-updating web dashboard.

---

## 🚀 System Architecture
The project utilizes a **Full-Stack IoT** approach to ensure zero-latency updates:
1. **Hardware Layer:** ESP8266 reads/writes to MIFARE 1K cards via SPI protocol.
2. **Communication Layer:** - **MQTT:** Handles device-to-broker messaging.
   - **WebSockets:** Handles server-to-browser live updates (No polling).
3. **Application Layer:** Node.js/Express dashboard for monitoring and top-ups.



---

## 🛠️ Hardware Connections
| MFRC522 Pin | ESP8266 Pin | Function |
| :--- | :--- | :--- |
| **SDA (CS)** | D2 (GPIO 4) | Chip Select |
| **SCK** | D5 (GPIO 14) | SPI Clock |
| **MOSI** | D7 (GPIO 13) | Master Out Slave In |
| **MISO** | D6 (GPIO 12) | Master In Slave Out |
| **RST** | D1 (GPIO 5) | Reset |
| **3.3V** | 3.3V | Power (Stable) |
| **GND** | GND | Ground |

---

## 💻 Software Implementation

### 1. Device Logic (MicroPython)
The device handles physical authentication using the **Factory Default Key (`0xFFFFFFFFFFFF`)**. It targets **Sector 2 (Block 8)** for data storage to avoid interference with manufacturer data.
* **Security:** Implements `auth()` handshake before any read/write operation.
* **Robustness:** Includes a `select_tag` check to ensure the card is present before processing.

### 2. Backend (Node.js)
The VPS server acts as a bridge. It subscribes to MQTT topics from the device and pushes data to the frontend via WebSockets.
* **Port:** `9216`
* **MQTT Topics:** - `rfid/ubuliza_david/card/status` (Device -> Web)
    - `rfid/ubuliza_david/card/topup` (Web -> Device)

### 3. Frontend (HTML5/CSS3)
A modern, responsive dashboard that updates automatically using the WebSocket `onmessage` event. 



---

## 📋 Features
- [x] **Live Scanning:** Instant UID detection on tap.
- [x] **Physical Write:** Top-up amounts are physically stored in the card's EEPROM.
- [x] **Auto-Update:** Dashboard reflects balance changes without refreshing.
- [x] **Secure Auth:** Uses encrypted sector authentication.

---

## 🔧 Installation
1. **Device:** Upload `mfrc522.py` and `main.py` to the ESP8266.
2. **Server:** ```bash
   npm install express mqtt ws
   node server.js
