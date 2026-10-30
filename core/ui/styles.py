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
            border-radius: 0px;
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
            border-radius: 0px;
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
            border-radius: 0px;
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
            border-radius: 0px;
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
            /* Degradado para volumen */
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #4A5568, stop:1 #2D3748
            );
            color: white;
            
            /* Bordes biselados */
            border: 1px solid #1A202C;
            border-top: 1px solid #718096;
            border-bottom: 2px solid #1A202C;
            border-radius: 6px;
            
            font-family: 'Segoe UI';
            font-size: 9pt;
            font-weight: 500;
            padding: 4px 10px;
        }
 
        QPushButton:hover {
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #5A6B8A, stop:1 #4A5568
            );
            border-top: 1px solid #A0AEC0;
        }
 
        QPushButton:pressed {
            /* Hundimiento */
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #1A202C, stop:1 #2D3748
            );
            border-top: 2px solid #1A202C;
            border-bottom: 1px solid #718096;
            
            /* Ajuste para simular clic */
            padding-top: 5px;
            padding-bottom: 3px;
        }
 
        QPushButton:disabled {
            background-color: #9CA3AF;
            color: #E5E7EB;
            
            /* Desactivar 3D cuando está deshabilitado */
            border: 1px solid #6B7280;
            border-top: 1px solid #6B7280;
            border-bottom: 1px solid #6B7280;
        }
    """
 
    FIXTURE_BUTTON_NOT_CONNECTED = """
        QPushButton {
            /* Degradado para dar volumen */
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #7C8594, stop:1 #6B7280
            );
            color: white;
            
            /* Borde biselado: claro arriba, oscuro abajo (Efecto 3D) */
            border: 1px solid #4B5563;
            border-top: 1px solid #9CA3AF;
            border-bottom: 2px solid #374151;
            border-radius: 4px;
            
            font-family: 'Segoe UI';
            font-size: 9pt;
            font-weight: 600;
            padding: 6px 10px;
        }
 
        QPushButton:hover {
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #8F9AA8, stop:1 #7C8594
            );
            border-top: 1px solid #D1D5DB;
        }
 
        QPushButton:pressed {
            /* Hundimiento: fondo más oscuro, bordes invertidos */
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #5A626E, stop:1 #4B5563
            );
            
            border-top: 2px solid #374151;
            border-bottom: 1px solid #9CA3AF;
            
            /* Texto baja 1px para simular el clic */
            padding-top: 7px;
            padding-bottom: 5px;
        }
    """
 
 

    FIXTURE_BUTTON_CONNECTING = """
        QPushButton {
            /* Degradado Naranja/Amarillo (3D) */
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #FBBF24, stop:1 #F59E0B
            );
            color: white;
            
            /* Bordes biselados: claro arriba, oscuro abajo */
            border: 1px solid #92400E;
            border-top: 1px solid #FDE68A;
            border-bottom: 2px solid #92400E;
            border-radius: 6px;
            
            font-family: 'Segoe UI';
            font-size: 9pt;
            font-weight: 500;
            padding: 4px 10px;
        }
 
        QPushButton:hover {
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #FCD34D, stop:1 #FBBF24
            );
            border-top: 1px solid #FEF08A;
        }
 
        QPushButton:pressed {
            /* Hundimiento */
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #D97706, stop:1 #B45309
            );
            border-top: 2px solid #92400E;
            border-bottom: 1px solid #FDE68A;
            padding-top: 5px;
            padding-bottom: 3px;
        }
    """
 

    FIXTURE_BUTTON_READY = """
        QPushButton {
            /* Degradado Verde (3D) */
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #22C55E, stop:1 #16A34A
            );
            color: white;
            
            /* Bordes biselados */
            border: 1px solid #14532D;
            border-top: 1px solid #4ADE80;
            border-bottom: 2px solid #14532D;
            border-radius: 6px;
            
            font-family: 'Segoe UI';
            font-size: 9pt;
            font-weight: 500;
            padding: 4px 10px;
        }
 
        QPushButton:hover {
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #4ADE80, stop:1 #22C55E
            );
            border-top: 1px solid #86EFAC;
        }
 
        QPushButton:pressed {
            /* Hundimiento */
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #15803D, stop:1 #166534
            );
            border-top: 2px solid #14532D;
            border-bottom: 1px solid #4ADE80;
            padding-top: 5px;
            padding-bottom: 3px;
        }
    """
 
    FIXTURE_BUTTON_FAILED = """
        QPushButton {
            /* Degradado Rojo (3D) */
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #EF4444, stop:1 #DC2626
            );
            color: white;
            
            /* Bordes biselados */
            border: 1px solid #7F1D1D;
            border-top: 1px solid #F87171;
            border-bottom: 2px solid #7F1D1D;
            border-radius: 6px;
            
            font-family: 'Segoe UI';
            font-size: 9pt;
            font-weight: 500;
            padding: 4px 10px;
        }
 
        QPushButton:hover {
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #F87171, stop:1 #EF4444
            );
            border-top: 1px solid #FCA5A5;
        }
 
        QPushButton:pressed {
            /* Hundimiento */
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #B91C1C, stop:1 #991B1B
            );
            border-top: 2px solid #7F1D1D;
            border-bottom: 1px solid #F87171;
            padding-top: 5px;
            padding-bottom: 3px;
        }
    """
 
    ANALYSIS_BUTTON = """
        QPushButton {
            /* Degradado para volumen (3D) */
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #4A5568, stop:1 #2D3748
            );
            color: white;
            
            /* Bordes biselados */
            border: 1px solid #1A202C;
            border-top: 1px solid #718096;
            border-bottom: 2px solid #1A202C;
            border-radius: 6px; /* Mismo redondeado que CONNECT */
            
            font-family: 'Segoe UI';
            font-size: 9pt;
            font-weight: 500;
            padding: 4px 10px;
        }
 
        QPushButton:hover {
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #5A6B8A, stop:1 #4A5568
            );
            border-top: 1px solid #A0AEC0;
        }
 
        QPushButton:pressed {
            /* Hundimiento al hacer clic */
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #1A202C, stop:1 #2D3748
            );
            border-top: 2px solid #1A202C;
            border-bottom: 1px solid #718096;
            
            /* Ajuste de padding para simular el clic */
            padding-top: 5px;
            padding-bottom: 3px;
        }
 
        QPushButton:disabled {
            background-color: #9CA3AF;
            color: #E5E7EB;
            border: 1px solid #6B7280;
            border-top: 1px solid #6B7280;
            border-bottom: 1px solid #6B7280;
            border-radius: 6px;
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

    EXPORT_RESULTS_BUTTON = """
        QPushButton {
            /* Degradado para volumen */
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #4A5568, stop:1 #2D3748
            );
            color: white;
            
            /* Bordes biselados */
            border: 1px solid #1A202C;
            border-top: 1px solid #718096;
            border-bottom: 2px solid #1A202C;
            border-radius: 6px;
            
            padding: 8px 16px;
            font-family: 'Segoe UI';
            font-size: 10pt;
            font-weight: 600;
        }
 
        QPushButton:hover {
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #5A6B8A, stop:1 #4A5568
            );
            border-top: 1px solid #A0AEC0;
        }
 
        QPushButton:pressed {
            /* Hundimiento */
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, 
                stop:0 #1A202C, stop:1 #2D3748
            );
            border-top: 2px solid #1A202C;
            border-bottom: 1px solid #718096;
            
            /* Ajuste sutil para simular clic */
            padding-top: 9px;
            padding-bottom: 7px;
        }
 
        QPushButton:disabled {
            background-color: #9CA3AF;
            color: #E5E7EB;
            border: 1px solid #6B7280;
            border-top: 1px solid #6B7280;
            border-bottom: 1px solid #6B7280;
        }
    """
 
 
