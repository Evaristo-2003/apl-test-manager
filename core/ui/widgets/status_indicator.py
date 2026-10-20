#!/usr/bin/env python3
"""Indicador de estado con colores"""

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt

class StatusIndicator(QLabel):
    """Indicador visual de estado"""
    
    COLORS = {
        "NOT CONNECTED": "#F1F0EC",
        "CONNECTING": "#FFC107",
        "READY": "#4CAF50",
        "FAILED": "#F44336",
        "RUNNING": "#FF9800"
    }
    
    def __init__(self, initial_status: str = "NOT CONNECTED", parent=None):
        super().__init__(parent)
        self._status = initial_status
        self.set_status(initial_status)
    
    def set_status(self, status: str):

        self._status = status

        styles = {

            "NOT CONNECTED": "⚫ NOT CONNECTED",
            "CONNECTING": "🟡 CONNECTING",
            "READY": "🟢 READY",
            "FAILED": "🔴 FAILED",
            "RUNNING": "🟠 RUNNING",
        }

        self.setText(
            styles.get(status, status)
        )

        self.setAlignment(Qt.AlignCenter)

        self.setStyleSheet("""
            QLabel {
                background-color: #F8F8F8;
                color: black;
                border-radius: 6px;
                border: 1px solid #C0C0C0;
                padding: 6px 12px;
                font-weight: bold;
            }
        """)
    @property
    def current_status(self):
        return self._status