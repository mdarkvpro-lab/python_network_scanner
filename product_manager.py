import sys, json, os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QInputDialog, QMessageBox, QHeaderView, QLabel, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

class ModernInventory(QWidget):
    def __init__(self):
        super().__init__()
        self.db_file = "inventory_master.json"
        self.setWindowTitle("Nova Inventory BI 2026")
        self.resize(1300, 850)
        
        # QSS Design: Dark Blue & Neon Purple Theme
        self.setStyleSheet("""
            QWidget { 
                background-color: #0b0e14; 
                color: #ffffff; 
                font-family: 'Inter', 'Segoe UI', sans-serif; 
            }
            QFrame#SidePanel { 
                background-color: #151921; 
                border-right: 1px solid #252a34; 
            }
            QFrame#StatCard {
                background-color: #1c222d;
                border: 1px solid #2d3446;
                border-radius: 12px;
                padding: 10px;
                margin: 5px 15px;
            }
            QLabel#Title { 
                font-size: 24px; font-weight: 800; color: #7b61ff; 
                padding: 25px; letter-spacing: 1px;
            }
            QPushButton {
                border-radius: 8px; padding: 12px; font-weight: bold; 
                font-size: 13px; margin: 5px 15px; border: 1px solid transparent;
            }
            QPushButton#AddBtn { background-color: #7b61ff; color: white; }
            QPushButton#AddBtn:hover { background-color: #6347ff; }
            
            QPushButton#SaveBtn { background-color: transparent; border: 1px solid #7b61ff; color: #7b61ff; }
            QPushButton#SaveBtn:hover { background-color: #7b61ff; color: white; }
            
            QPushButton#DelBtn { background-color: transparent; border: 1px solid #ff4757; color: #ff4757; }
            QPushButton#DelBtn:hover { background-color: #ff4757; color: white; }

            QTableWidget { 
                background-color: #0b0e14; gridline-color: #1c222d; 
                border: none; selection-background-color: #1c222d; 
                font-size: 14px;
            }
            QHeaderView::section { 
                background-color: #0b0e14; color: #8e9aaf; 
                padding: 15px; border: none; font-weight: bold;
                border-bottom: 2px solid #252a34;
            }
        """)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Side Panel
        self.side_panel = QFrame(); self.side_panel.setObjectName("SidePanel")
        self.side_panel.setFixedWidth(320)
        side_layout = QVBoxLayout()

        self.title_label = QLabel("NOVA BI"); self.title_label.setObjectName("Title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_add = QPushButton("＋  CREATE PRODUCT"); self.btn_add.setObjectName("AddBtn")
        self.btn_add.clicked.connect(self.run_questionnaire)

        self.btn_save = QPushButton("💾  SYNC DATABASE"); self.btn_save.setObjectName("SaveBtn")
        self.btn_save.clicked.connect(self.manual_save)

        self.btn_delete = QPushButton("🗑  REMOVE ITEM"); self.btn_delete.setObjectName("DelBtn")
        self.btn_delete.clicked.connect(self.delete_item)

        # Stats Cards
        side_layout.addWidget(self.title_label)
        side_layout.addWidget(self.btn_add)
        side_layout.addWidget(self.btn_save)
        side_layout.addWidget(self.btn_delete)
        
        side_layout.addSpacing(30)
        
        self.card_inv = self.create_stat_card("INVESTMENT", "0.00 DHS", "#00d2ff")
        self.card_rev = self.create_stat_card("EST. REVENUE", "0.00 DHS", "#7b61ff")
        self.card_prof = self.create_stat_card("NET PROFIT", "0.00 DHS", "#2ecc71")
        
        side_layout.addWidget(self.card_inv)
        side_layout.addWidget(self.card_rev)
        side_layout.addWidget(self.card_prof)
        
        side_layout.addStretch()
        self.side_panel.setLayout(side_layout)

        # Table Area
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["PRODUCT", "CATEGORY", "COST", "MARKUP", "SELL PRICE", "STOCK"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { alternate-background-color: #11151c; }")
        
        main_layout.addWidget(self.side_panel)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

    def create_stat_card(self, title, value, color):
        card = QFrame(); card.setObjectName("StatCard")
        layout = QVBoxLayout()
        t_lbl = QLabel(title); t_lbl.setStyleSheet(f"color: #8e9aaf; font-size: 10px; font-weight: bold;")
        v_lbl = QLabel(value); v_lbl.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
        layout.addWidget(t_lbl); layout.addWidget(v_lbl)
        card.setLayout(layout)
        # Store label reference for updates
        if "INVESTMENT" in title: self.lbl_inv = v_lbl
        elif "REVENUE" in title: self.lbl_rev = v_lbl
        else: self.lbl_prof = v_lbl
        return card

    def update_analytics(self):
        t_cost, t_rev = 0.0, 0.0
        for r in range(self.table.rowCount()):
            try:
                c = float(self.table.item(r, 2).text())
                m = float(self.table.item(r, 3).text())
                q = int(self.table.item(r, 5).text())
                sp = c * (1 + m/100)
                t_cost += (c * q)
                t_rev += (sp * q)
                # Update sell price in table
                self.table.item(r, 4).setText(f"{sp:.2f}")
            except: continue
        
        self.lbl_inv.setText(f"{t_cost:,.2f} DHS")
        self.lbl_rev.setText(f"{t_rev:,.2f} DHS")
        self.lbl_prof.setText(f"{(t_rev - t_cost):,.2f} DHS")

    def run_questionnaire(self):
        name, ok1 = QInputDialog.getText(self, "Nova Entry", "Product Name:")
        if not (ok1 and name.strip()): return
        cat, ok2 = QInputDialog.getItem(self, "Nova Entry", "Category:", ["Electronics", "Food", "Clothing", "Other"], 0, False)
        if not ok2: return
        cost, ok3 = QInputDialog.getDouble(self, "Nova Entry", "Cost Price (DH):", min=0.0)
        if not ok3: return
        markup, ok4 = QInputDialog.getDouble(self, "Nova Entry", "Markup %:", value=20.0, min=0.0)
        if not ok4: return
        stock, ok5 = QInputDialog.getInt(self, "Nova Entry", "Stock Qty:", min=0)
        if not ok5: return

        self.add_row_to_table(name, cat, cost, markup, stock)
        self.update_analytics()

    def add_row_to_table(self, name, cat, cost, markup, stock):
        row = self.table.rowCount()
        self.table.insertRow(row)
        sp = cost * (1 + markup/100)
        data = [name, cat, str(cost), str(markup), f"{sp:.2f}", str(stock)]
        for i, v in enumerate(data):
            item = QTableWidgetItem(v)
            if i in [0, 1, 4]: item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            if i == 4: item.setForeground(QColor("#00d2ff"))
            self.table.setItem(row, i, item)

    def manual_save(self):
        data = []
        for r in range(self.table.rowCount()):
            data.append({"n": self.table.item(r,0).text(), "c": self.table.item(r,1).text(), 
                         "co": self.table.item(r,2).text(), "m": self.table.item(r,3).text(), "s": self.table.item(r,5).text()})
        with open(self.db_file, "w") as f: json.dump(data, f)
        self.update_analytics()
        QMessageBox.information(self, "Sync", "Cloud Database Synchronized.")

    def delete_item(self):
        if self.table.currentRow() >= 0:
            self.table.removeRow(self.table.currentRow())
            self.update_analytics()

    def load_data(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, "r") as f:
                try:
                    for i in json.load(f): self.add_row_to_table(i["n"], i["c"], float(i["co"]), float(i["m"]), int(i["s"]))
                    self.update_analytics()
                except: pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernInventory(); window.show()
    sys.exit(app.exec())