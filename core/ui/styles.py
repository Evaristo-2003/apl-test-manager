#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Estilos centralizados de la aplicación"""

class AppStyles:
    """Estilos globales de la aplicación"""
    
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