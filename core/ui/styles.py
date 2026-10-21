#!/usr/bin/env python3
"""Estilos centralizados de la aplicación"""


class AppStyles:
    """Estilos globales"""

    MAIN = """
        QMainWindow {
            background: #F3F2F1;
        }

        QGroupBox {
            font-weight: bold;
            color: #323130;
            background: white;
            border: 1px solid #D2D0CE;
            border-radius: 10px;
            margin-top: 10px;
            padding-top: 10px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }

        QPushButton {
            border-radius: 0px;
            font-family: 'Segoe UI';
            font-size: 9pt;
            font-weight: 500;
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
            background-color: #2D3748;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            padding: 8px;
        }

        QPushButton:hover {
            background-color: #4A5568;
        }

        QPushButton:pressed {
            background-color: #0D47A1;
        }
    """
    LOADSAPME_BUTTON = """
        QPushButton {
            background-color: #2D3748;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            padding: 8px;
        }

        QPushButton:hover {
            background-color: #4A5568;
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
            background-color: #2D3748;
            color: white;
            font-size: 14px;
            font-weight: bold;
            padding: 15px;
            border-radius: 8px;
        }

        QPushButton:hover {
            background-color: #4A5568;
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

        background-color: #2D3748;
        color: white;

        border: 1px solid #1A202C;
        border-radius: 0px;

        font-family: 'Segoe UI';
        font-size: 9pt;
        font-weight: 500;

        padding: 4px 10px;

        text-align: left;
    }

    QPushButton:hover {

        background-color: #4A5568;
    }

    QPushButton:pressed {

        background-color: #1A202C;
    }
    """
    RUN_ALL_BUTTON = """
    QPushButton {

        background-color: #2D3748;
        color: white;

        border: 1px solid #1A202C;
        border-radius: 0px;

        font-family: 'Segoe UI';
        font-size: 9pt;
        font-weight: 500;

        padding: 4px 10px;
    }

    QPushButton:hover {

        background-color: #4A5568;
    }

    QPushButton:pressed {

        background-color: #1A202C;
    }

    QPushButton:disabled {

        background-color: #9CA3AF;
        color: #E5E7EB;
    }
    """
    FIXTURE_BUTTON_NOT_CONNECTED = """
    QPushButton {

        background-color: #6B7280;
        color: white;

        border: 1px solid #1A202C;
        border-radius: 0px;

        font-family: 'Segoe UI';
        font-size: 9pt;
        font-weight: 500;

        padding: 4px 10px;
    }
    """

    FIXTURE_BUTTON_CONNECTING = """
    QPushButton {

        background-color: #F59E0B;
        color: white;

        border: 1px solid #1A202C;
        border-radius: 0px;

        font-family: 'Segoe UI';
        font-size: 9pt;
        font-weight: 500;

        padding: 4px 10px;
    }
    """

    FIXTURE_BUTTON_READY = """
    QPushButton {

        background-color: #16A34A;
        color: white;

        border: 1px solid #1A202C;
        border-radius: 0px;

        font-family: 'Segoe UI';
        font-size: 9pt;
        font-weight: 500;

        padding: 4px 10px;
    }
    """


    FIXTURE_BUTTON_FAILED = """
    QPushButton {

        background-color: #DC2626;
        color: white;

        border: 1px solid #1A202C;
        border-radius: 0px;

        font-family: 'Segoe UI';
        font-size: 9pt;
        font-weight: 500;

        padding: 4px 10px;
    }
    """

    ANALYSIS_BUTTON = """
    QPushButton {

        background-color: #2D3748;
        color: white;

        border: 1px solid #1A202C;
        border-radius: 0px;

        font-family: 'Segoe UI';
        font-size: 9pt;
        font-weight: 500;

        padding: 4px 10px;
    }

    QPushButton:hover {

        background-color: #4A5568;
    }

    QPushButton:pressed {

        background-color: #1A202C;
    }
    """

    DASHBOARD_RUN_ALL_BUTTON = """
        QPushButton {
            background-color: #2D3748;
            color: white;
            font-size: 14px;
            font-weight: bold;
            padding: 15px;
            border-radius: 8px;
        }

        QPushButton:hover {
            background-color: #4A5568;
        }

        QPushButton:pressed {
            background-color: #0D47A1;
        }

        QPushButton:disabled {
            background-color: #757575;
            color: white;
        }
    """