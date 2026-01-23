import sys
import os
import threading
import subprocess
import re

# --- [ EXE FIX: STDOUT REDIRECTION ] ---
# هاد الكود ضروري باش الـ Speedtest ما يكراشيش فاش كترجع البرنامج .exe
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QTextEdit, QLabel)
from PyQt6.QtCore import Qt, QMetaObject, Q_ARG
from scapy.all import ARP, Ether, srp
import speedtest # pip install speedtest-cli

class UltimateScannerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("VENOM_TACTICAL_SCANNER_V5.1")
        self.setFixedSize(800, 700)
        self.setStyleSheet("""
            QMainWindow { background-color: #050505; }
            QLabel { color: #00f2ff; font-family: 'Consolas'; font-size: 14px; font-weight: bold; }
            QTextEdit { 
                background-color: #000; border: 1px solid #00f2ff; 
                color: #0dff00; font-family: 'Consolas'; font-size: 11px; 
            }
            QPushButton { 
                background-color: #00f2ff; color: #000; font-weight: bold; 
                padding: 12px; border-radius: 5px; font-family: 'Consolas';
            }
            QPushButton:hover { background-color: #008c95; }
            QPushButton:disabled { background-color: #111; color: #444; }
        """)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.layout.addWidget(QLabel(">> SPECTRUM_ANALYSIS: FULL_HYBRID_SCAN"))
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.layout.addWidget(self.console)

        self.scan_btn = QPushButton("INITIATE_DEEP_SCAN")
        self.scan_btn.clicked.connect(self.start_full_scan)
        self.layout.addWidget(self.scan_btn)

    def log(self, message):
        QMetaObject.invokeMethod(self.console, "append", Qt.ConnectionType.QueuedConnection, Q_ARG(str, message))

    def start_full_scan(self):
        self.scan_btn.setEnabled(False)
        self.console.clear()
        threading.Thread(target=self.run_logic, daemon=True).start()

    def get_all_wifi_networks(self):
        """Deep Scan for every SSID using Windows Netsh"""
        try:
            process = subprocess.check_output(['netsh', 'wlan', 'show', 'networks', 'mode=bssid'], 
                                           shell=True, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
            results = process.decode('ascii', errors='ignore')
            
            networks = []
            current_ssid = ""
            for line in results.split('\n'):
                line = line.strip()
                if line.startswith("SSID"):
                    current_ssid = line.split(":", 1)[1].strip() or "[HIDDEN_NETWORK]"
                if "Signal" in line:
                    signal_val = int(line.split(":", 1)[1].strip().replace("%", ""))
                    networks.append((current_ssid, signal_val))
            
            networks.sort(key=lambda x: x[1], reverse=True)
            return [f"{ssid:<25} | SIGNAL: {sig}%" for ssid, sig in networks]
        except: return ["[!] DEEP_SCAN_FAILED"]

    def get_speed_test(self):
        """Measures bandwidth speed accurately"""
        try:
            self.log("[*] ANALYZING_BANDWIDTH (Stay connected)...")
            st = speedtest.Speedtest(secure=True)
            st.get_best_server()
            dw = st.download() / 1_000_000
            up = st.upload() / 1_000_000
            return f"DW: {dw:.2f} Mbps | UP: {up:.2f} Mbps"
        except Exception as e:
            return f"SPEED_TEST_ERROR: {str(e)}"

    def run_logic(self):
        # Stage 1: WiFi
        self.log("[1] DETECTING_ALL_WIFI_CHANNELS...")
        wifi_list = self.get_all_wifi_networks()
        for net in wifi_list:
            prefix = "[HIGH]" if "100" in net or "9" in net[:2] else "[SCAN]"
            self.log(f" {prefix} {net}")
        self.log(f"\n[+] TOTAL_NETWORKS_FOUND: {len(wifi_list)}")
        self.log("-" * 60)

        # Stage 2: ARP Scan (Network Devices)
        self.log("[2] MAPPING_LOCAL_DEVICES...")
        try:
            ans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst="192.168.1.1/24"), timeout=2, verbose=False)[0]
            for s, r in ans:
                self.log(f" [HOST] IP: {r.psrc:<15} | MAC: {r.hwsrc}")
        except: 
            self.log(" [!] ARP_FAILURE: MAKE SURE TO RUN AS ADMINISTRATOR")

        # Stage 3: Speed Test
        self.log("\n[3] TESTING_INTERNET_VELOCITY...")
        self.log(f" [SPEED] {self.get_speed_test()}")

        self.log("\n[*] ALL_SYSTEMS_NOMINAL. OPERATION_COMPLETE.")
        QMetaObject.invokeMethod(self.scan_btn, "setEnabled", Qt.ConnectionType.QueuedConnection, Q_ARG(bool, True))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UltimateScannerUI()
    window.show()
    sys.exit(app.exec())