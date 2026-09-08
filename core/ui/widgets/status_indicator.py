#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Indicador de estado con colores"""

from PySide6.QtWidgets import QLabel


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
        """Actualiza el estado"""
        self._status = status
        color = self.COLORS.get(status, "#F1F0EC")
        self.setText(status)
        self.setStyleSheet(f"""
            background: {color};
            border: 2px solid black;
            padding: 8px;
            font-weight: bold;
        """)