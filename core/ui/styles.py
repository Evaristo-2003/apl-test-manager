#!/usr/bin/env python3
"""Estilos centralizados de la aplicación"""


class AppStyles:
    """Estilos globales"""

    MAIN = """
        QMainWindow {
            background: #f5f5f5;
        }

        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }

        QPushButton {
            background: #2196F3;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 4px;
            font-weight: bold;
        }

        QPushButton:hover {
            background: #1976D2;
        }

        QPushButton:pressed {
            background: #0D47A1;
        }

        QListWidget {
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 5px;
        }

        QListWidget::item {
            padding: 5px;
        }

        QListWidget::item:selected {
            background: #2196F3;
            color: white;
        }

        QTextEdit {
            border: 1px solid #cccccc;
            border-radius: 4px;
            font-family: monospace;
            font-size: 11px;
        }
    """

    DARK = """
        QMainWindow {
            background: #1e1e1e;
        }

        QGroupBox {
            color: #ffffff;
            border-color: #444444;
        }

        QPushButton {
            background: #333333;
            color: #ffffff;
        }

        QPushButton:hover {
            background: #444444;
        }

        QListWidget {
            background: #2d2d2d;
            color: #ffffff;
            border-color: #444444;
        }

        QTextEdit {
            background: #2d2d2d;
            color: #d4d4d4;
            border-color: #444444;
        }
    """

    # ----------------------------------
    # FIXTURE CONTROL
    # ----------------------------------

    CONNECT_BUTTON = """
        QPushButton {
            background-color: #2E7D32;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            padding: 8px;
        }

        QPushButton:hover {
            background-color: #388E3C;
        }

        QPushButton:pressed {
            background-color: #1B5E20;
        }
    """

    DISCONNECT_BUTTON = """
        QPushButton {
            background-color: #C62828;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            padding: 8px;
        }

        QPushButton:hover {
            background-color: #D32F2F;
        }

        QPushButton:pressed {
            background-color: #B71C1C;
        }
    """

    REFRESH_BUTTON = """
        QPushButton {
            background-color: #1565C0;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            padding: 8px;
        }

        QPushButton:hover {
            background-color: #1976D2;
        }

        QPushButton:pressed {
            background-color: #0D47A1;
        }
    """

    # ----------------------------------
    # TEST ACTIONS
    # ----------------------------------

    RUN_TEST_BUTTON = """
        QPushButton {
            background-color: #1565C0;
            color: white;
            font-size: 14px;
            font-weight: bold;
            padding: 15px;
            border-radius: 8px;
        }

        QPushButton:hover {
            background-color: #1976D2;
        }

        QPushButton:pressed {
            background-color: #0D47A1;
        }
    """

    RUN_ALL_BUTTON = """
        QPushButton {
            background-color: #1565C0;
            color: white;
            font-size: 14px;
            font-weight: bold;
            padding: 15px;
            border-radius: 8px;
        }

        QPushButton:hover {
            background-color: #1976D2;
        }

        QPushButton:pressed {
            background-color: #0D47A1;
        }
    """

    # ----------------------------------
    # DASHBOARD GROUPS
    # ----------------------------------

    GROUP_HEADER = """
        QPushButton {
            text-align: left;
            font-size: 14px;
            font-weight: bold;
            padding: 8px;
            background-color: #2D3748;
            color: white;
            border-radius: 6px;
        }

        QPushButton:hover {
            background-color: #4A5568;
        }
    """