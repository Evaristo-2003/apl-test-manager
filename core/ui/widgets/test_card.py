#!/usr/bin/env python3
"""Widget de tarjeta de prueba para dashboard"""

from PySide6.QtCore import Qt,Signal
from PySide6.QtWidgets import QPushButton


class TestCard(QPushButton):
    """Tarjeta de prueba en el dashboard"""
    rightClicked = Signal(str) 
    # Colores por estado
    COLORS = {
        "NOT_RUN": "#F5F5F5",
        "RUNNING": "#FFE699",
        "PASS": "#C6EFCE",
        "FAIL": "#FFC7CE",
        "WARNING": "#FFE699"
    }
    
    def __init__(self, test_name: str, parent=None):
        super().__init__(parent)
        self.test_name = test_name
        self._status = "NOT_RUN"
        self.setFixedSize(170, 80)
        self.setCursor(Qt.PointingHandCursor)
        self.update_display()
    
    def set_status(self, status: str):
        """Actualiza el estado de la tarjeta"""
        self._status = status
        self.update_display()
    
    def update_display(self):
        """Actualiza la apariencia de la tarjeta"""

        color = self.COLORS.get(
            self._status,
            "#F1F0EC"
        )

        self.setText(
            f"{self.test_name}\n\n{self._status}"
        )

        self.setStyleSheet(f"""
            QPushButton {{

                background-color: {color};

                color: #202020;

                border: 1px solid #2D3748;
                border-radius: 0px;

                font-family: "Segoe UI";
                font-size: 9pt;
                font-weight: 500;

                padding: 6px;
                text-align: center;
            }}

            QPushButton:hover {{

                border: 2px solid #3182CE;
            }}

            QPushButton:pressed {{

                background-color: #DDEAF2;
            }}
        """)

    def mousePressEvent(self, event):

        if event.button() == Qt.RightButton:

            self.rightClicked.emit(
                self.test_name
            )

            return

        super().mousePressEvent(event)