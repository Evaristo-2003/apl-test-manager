#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Widget de tarjeta de prueba para dashboard"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, Signal


class TestCard(QPushButton):
    """Tarjeta de prueba en el dashboard"""
    
    # Colores por estado
    COLORS = {
        "NOT_RUN": "#F1F0EC",
        "RUNNING": "#FFC107",
        "PASS": "#4CAF50",
        "FAIL": "#F44336",
        "WARNING": "#FF9800"
    }
    
    def __init__(self, test_name: str, parent=None):
        super().__init__(parent)
        self.test_name = test_name
        self._status = "NOT_RUN"
        self.setFixedSize(180, 100)
        self.setCursor(Qt.PointingHandCursor)
        self.update_display()
    
    def set_status(self, status: str):
        """Actualiza el estado de la tarjeta"""
        self._status = status
        self.update_display()
    
    def update_display(self):
        """Actualiza la apariencia de la tarjeta"""
        color = self.COLORS.get(self._status, "#F1F0EC")
        self.setText(f"{self.test_name}\n\n{self._status}")
        self.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                border: 2px solid black;
                border-radius: 12px;
                padding: 20px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                border: 3px solid #0078d7;
            }}
            QPushButton:pressed {{
                background: #d6ebff;
            }}
        """)