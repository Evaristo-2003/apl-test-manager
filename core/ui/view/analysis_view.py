#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vista de Analysis - Captura continua de logs AB/CB"""

import os
import time
import threading
from datetime import datetime

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QTextBrowser,
    QGroupBox,
)

from core.adapters.serial_adapter import SerialAdapter
from core.ui.styles import AppStyles


class LogSignals(QObject):
    """Señales para comunicación entre hilos de captura y UI."""
    cb_text = Signal(str)
    ab_text = Signal(str)


class AnalysisView(QWidget):
    """
    Vista de Analysis para diagnóstico AB/CB.
    
    Permite:
        - Conectar CB y AB por COM
        - Capturar logs continuos de ambos puertos
        - Guardar logs combinados
        - Ejecutar "AB CONNECTION" (power on AB)
    """

    def __init__(self,fixture_controller):
        super().__init__()

        # Inicializar controlador de fixture
        self.fixture_controller = (fixture_controller)
        # Adaptadores
        self.cb_adapter = SerialAdapter()
        self.ab_adapter = SerialAdapter()

        # Flags de captura
        self.cb_capture_running = False
        self.ab_capture_running = False

        # Buffers de log
        self.cb_log_buffer = []
        self.ab_log_buffer = []

        # Señales Qt (para actualizar UI desde hilos)
        self.signals = LogSignals()

        # Construir UI
        self._build_ui()

        # Conectar señales a consolas
        self.signals.cb_text.connect(self.cb_console.insertPlainText)
        self.signals.ab_text.connect(self.ab_console.insertPlainText)
        self.refresh_ports()
    # ============================================================
    # CONSTRUCCIÓN DE UI
    # ============================================================

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --------------------------
        # ANALYSIS ACTIONS
        # --------------------------
        actions_layout = QHBoxLayout()
        self.btn_refresh_ports = QPushButton(
            "REFRESH PORTS"
        )

        self.btn_refresh_ports.setStyleSheet(
            AppStyles.RUN_ALL_BUTTON
        )

        self.btn_refresh_ports.setFixedHeight(
            28
        )

        self.btn_ab_connection = QPushButton(
            "AB CONNECTION"
        )

        self.btn_ab_connection.setStyleSheet(
            AppStyles.RUN_ALL_BUTTON
        )

        self.btn_ab_connection.setFixedHeight(
            28
        )

        self.btn_clear_terminal = QPushButton(
            "CLEAR TERMINAL"
        )

        self.btn_clear_terminal.setStyleSheet(
            AppStyles.RUN_ALL_BUTTON
        )

        self.btn_clear_terminal.setFixedHeight(
            28
        )

        self.btn_save_log = QPushButton(
            "SAVE LOG"
        )

        self.btn_save_log.setStyleSheet(
            AppStyles.RUN_ALL_BUTTON
        )

        self.btn_save_log.setFixedHeight(
            28
        )

        self.btn_disconnect = QPushButton(
            "DISCONNECT"
        )

        self.btn_disconnect.setStyleSheet(
            AppStyles.RUN_ALL_BUTTON
        )

        self.btn_disconnect.setFixedHeight(
            28
        )

        actions_layout.addStretch()

        actions_layout.addWidget(
            self.btn_ab_connection
        )

        actions_layout.addWidget(
            self.btn_refresh_ports
        )

        actions_layout.addWidget(
            self.btn_clear_terminal
        )

        actions_layout.addWidget(
            self.btn_save_log
        )

        actions_layout.addWidget(
            self.btn_disconnect
        )

        layout.addLayout(
            actions_layout
        )

        # --------------------------
        # CB BOARD
        # --------------------------
        self.cb_group = QGroupBox("CB BOARD")
        cb_layout = QVBoxLayout(self.cb_group)
        cb_layout.setContentsMargins(8, 8, 8, 8)
        cb_layout.setSpacing(6)

        self.lbl_cb_status = QLabel("STATUS: DISCONNECTED")
        self.lbl_cb_status.setStyleSheet("""
            font-weight: bold;
            color: #404040;
        """)
        cb_layout.addWidget(self.lbl_cb_status)

        cb_top = QHBoxLayout()

        cb_top.addWidget(QLabel("COM:"))

        self.cb_combo = QComboBox()
        self.cb_combo.setMinimumWidth(200)
        cb_top.addWidget(self.cb_combo)

        self.btn_cb_connect = QPushButton("CONNECT")
        self.btn_cb_connect.setStyleSheet(AppStyles.ANALYSIS_BUTTON)
        cb_top.addWidget(self.btn_cb_connect)

        self.btn_cb_kill = QPushButton("KILL WSSC")
        self.btn_cb_kill.setStyleSheet(AppStyles.ANALYSIS_BUTTON)
        cb_top.addWidget(self.btn_cb_kill)

        self.btn_cb_power_off = QPushButton("POWER OFF")
        self.btn_cb_power_off.setStyleSheet(AppStyles.ANALYSIS_BUTTON)
        cb_top.addWidget(self.btn_cb_power_off)
        
        cb_top.addStretch()
        cb_layout.addLayout(cb_top)

        self.cb_console = QTextBrowser()
        self.cb_console.setPlaceholderText("CB console output...")
        cb_layout.addWidget(self.cb_console)

        layout.addWidget(self.cb_group)

        # --------------------------
        # AB BOARD
        # --------------------------
        self.ab_group = QGroupBox("AB BOARD")
        ab_layout = QVBoxLayout(self.ab_group)
        ab_layout.setContentsMargins(8, 8, 8, 8)
        ab_layout.setSpacing(6)

        self.lbl_ab_status = QLabel("STATUS: DISCONNECTED")
        self.lbl_ab_status.setStyleSheet("""
            font-weight: bold;
            color: #404040;
        """)
        ab_layout.addWidget(self.lbl_ab_status)

        ab_top = QHBoxLayout()

        ab_top.addWidget(QLabel("COM:"))

        self.ab_combo = QComboBox()
        self.ab_combo.setMinimumWidth(200)
        ab_top.addWidget(self.ab_combo)

        self.btn_ab_connect = QPushButton("CONNECT")
        self.btn_ab_connect.setStyleSheet(AppStyles.ANALYSIS_BUTTON)
        ab_top.addWidget(self.btn_ab_connect)

        self.btn_ab_kill = QPushButton("KILL WSSC")
        self.btn_ab_kill.setStyleSheet(AppStyles.ANALYSIS_BUTTON)
        ab_top.addWidget(self.btn_ab_kill)

        ab_top.addStretch()
        ab_layout.addLayout(ab_top)

        self.ab_console = QTextBrowser()
        self.ab_console.setPlaceholderText("AB console output...")
        ab_layout.addWidget(self.ab_console)

        layout.addWidget(self.ab_group)

        layout.addStretch()

        # --------------------------
        # CONEXIONES
        # --------------------------
        self.btn_refresh_ports.clicked.connect(self.refresh_ports)
        self.btn_cb_connect.clicked.connect(self.connect_cb)
        self.btn_ab_connect.clicked.connect(self.connect_ab)
        self.btn_cb_kill.clicked.connect(self.kill_cb_wssc)
        self.btn_cb_power_off.clicked.connect(self.power_off_cb)
        self.btn_ab_kill.clicked.connect(self.kill_ab_wssc)
        self.btn_ab_connection.clicked.connect(self.start_ab_connection_analysis)
        self.btn_save_log.clicked.connect(self.save_log)
        self.btn_disconnect.clicked.connect(self.disconnect_all)
        self.btn_clear_terminal.clicked.connect(self.clear_terminal)

    # ============================================================
    # UTILIDADES
    # ============================================================

    def set_ports(self, ports):
        """Carga la lista de puertos COM en ambos combos."""
        self.cb_combo.clear()
        self.ab_combo.clear()
        self.cb_combo.addItems(ports)
        self.ab_combo.addItems(ports)

    def refresh_ports(self):
        """Refresca la lista de puertos disponibles."""
        ports = SerialAdapter.get_available_ports()
        self.set_ports(ports)
        self.cb_console.append(f"Available ports: {ports}")
        self.ab_console.append(f"Available ports: {ports}")

    # ============================================================
    # CONEXIÓN
    # ============================================================

    def connect_cb(self):
        """Conecta al puerto CB."""
        if self.cb_adapter.is_connected():
            self.cb_console.append(f"Already connected to {self.cb_adapter.port}")
            return

        port = self.cb_combo.currentText()
        if not port:
            return

        ok = self.cb_adapter.connect(port)

        if ok:
            self.lbl_cb_status.setText("STATUS: CONNECTED")
            self.lbl_cb_status.setStyleSheet("""
                color: #16A34A;
                font-weight: 600;
            """)
            self.cb_console.append(f"Connected to {port}")
            self.start_cb_capture()
        else:
            self.lbl_cb_status.setText("STATUS: FAILED")
            self.lbl_cb_status.setStyleSheet("""
                color: #DC2626;
                font-weight: 600;
            """)
            self.cb_console.append(f"Failed to connect to {port}")

    def connect_ab(self):
        """Conecta al puerto AB."""
        if self.ab_adapter.is_connected():
            self.ab_console.append(f"Already connected to {self.ab_adapter.port}")
            return

        port = self.ab_combo.currentText()
        if not port:
            return

        ok = self.ab_adapter.connect(port)

        if ok:
            self.lbl_ab_status.setText("STATUS: CONNECTED")
            self.lbl_ab_status.setStyleSheet("""
                color: #16A34A;
                font-weight: 600;
            """)
            self.ab_console.append(f"Connected to {port}")
            self.start_ab_capture()
        else:
            self.lbl_ab_status.setText("STATUS: FAILED")
            self.lbl_ab_status.setStyleSheet("""
                color: #DC2626;
                font-weight: 600;
            """)
            self.ab_console.append(f"Failed to connect to {port}")

    # ============================================================
    # CAPTURA CONTINUA
    # ============================================================

    def start_cb_capture(self):
        """Inicia captura continua del puerto CB."""
        if self.cb_capture_running:
            return

        self.cb_capture_running = True

        def worker():
            while self.cb_capture_running and self.cb_adapter.is_connected():
                try:
                    if self.cb_adapter._serial.in_waiting:
                        data = self.cb_adapter._serial.read(
                            self.cb_adapter._serial.in_waiting
                        ).decode("utf-8", errors="ignore")

                        if data:
                            self.cb_log_buffer.append(data)
                            # Emitir por señal (thread-safe)
                            self.signals.cb_text.emit(data)
                    time.sleep(0.01)
                except Exception:
                    break

        threading.Thread(target=worker, daemon=True).start()

    def start_ab_capture(self):
        """Inicia captura continua del puerto AB."""
        if self.ab_capture_running:
            return

        self.ab_capture_running = True

        def worker():
            while self.ab_capture_running and self.ab_adapter.is_connected():
                try:
                    if self.ab_adapter._serial.in_waiting:
                        data = self.ab_adapter._serial.read(
                            self.ab_adapter._serial.in_waiting
                        ).decode("utf-8", errors="ignore")

                        if data:
                            self.ab_log_buffer.append(data)
                            # Emitir por señal (thread-safe)
                            self.signals.ab_text.emit(data)
                    time.sleep(0.01)
                except Exception:
                    break

        threading.Thread(target=worker, daemon=True).start()

    # ============================================================
    # KILL WSSC
    # ============================================================

    def kill_cb_wssc(self):
        """Envía comando para matar WSSC en CB."""
        if not self.cb_adapter.is_connected():
            return

        self.cb_adapter.send_command("hotkey_wssc.sh 0")
        self.cb_console.append("\n[KILL WSSC sent to CB]\n")

    def kill_ab_wssc(self):
        """Envía comando para matar WSSC en AB."""
        if not self.ab_adapter.is_connected():
            return

        self.ab_adapter.send_command("hotkey_wssc.sh 0")
        self.ab_console.append("\n[KILL WSSC sent to AB]\n")

    # ============================================================
    # AB CONNECTION (Power On)
    # ============================================================

    def start_ab_connection_analysis(self):
        """Ejecuta el flujo de AB CONNECTION."""
        if not self.cb_adapter.is_connected():
            self.cb_console.append("\n[ERROR] CB NOT CONNECTED\n")
            return

        if not self.ab_adapter.is_connected():
            self.ab_console.append("\n[ERROR] AB NOT CONNECTED\n")
            return

        # Limpiar buffers
#        self.cb_log_buffer.clear()
#        self.ab_log_buffer.clear()

        # Limpiar consolas
#        self.cb_console.clear()
#        self.ab_console.clear()

        # Encabezados
        self.cb_console.append("========== AB CONNECTION TEST ==========")
        self.ab_console.append("========== AB CONNECTION TEST ==========")

        # Enviar power on
        self.cb_adapter.send_command("pwr_on_intl.sh 1")

    # ============================================================
    # SAVE LOG
    # ============================================================

    def save_log(self):
        """Guarda el log combinado AB + CB en archivo."""
        # Crear carpeta si no existe
        os.makedirs("analysis_logs", exist_ok=True)

        # Timestamp
        from core.state.app_state import app_state

        sfc = getattr(
            app_state,
            "current_sfc",
            ""
        ).strip()

        project = (
            getattr(
                app_state,
                "project",
                "UNKNOWN"
            )
            .strip()
            .replace(" ", "_")
        )

        if sfc:

            filename = (
                f"analysis_logs/"
                f"{sfc}_{project}.log"
            )

        else:

            filename = (
                f"analysis_logs/"
                f"NO_SFC_{project}.log"
            )

        cb_content = "".join(self.cb_log_buffer)
        ab_content = "".join(self.ab_log_buffer)
        cb_content = cb_content.strip()
        ab_content = ab_content.strip()
        content = (
            "==================================================\n"
            "CB LOG\n"
            "==================================================\n\n"
            f"{cb_content}\n\n"
            "==================================================\n"
            "AB LOG\n"
            "==================================================\n\n"
            f"{ab_content}\n"
        )

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        #
        # Limpiar buffers
        #
        self.cb_log_buffer.clear()
        self.ab_log_buffer.clear()

        #
        # Limpiar consolas
        #
        self.cb_console.clear()
        self.ab_console.clear()
        self.cb_console.append(f"\n[SAVE LOG] Saved to {filename}\n")
        self.ab_console.append(f"\n[SAVE LOG] Saved to {filename}\n")
  
    # ============================================================
    # DISCONNECT ALL
    # ============================================================
    def disconnect_all(self):

        #
        # Detener capturas
        #
        self.cb_capture_running = False
        self.ab_capture_running = False

        #
        # Erase DID
        #
        if self.ab_adapter.is_connected():

            self.ab_console.append(
                "\n[ERASING DID]\n"
            )

            response = (
                self.ab_adapter.execute_command_until(
                    "websocket_test.sh erasedid",
                    "ERASE DID/PDR SUCCESS",
                    30
                )
            )

            self.ab_console.append(
                response
            )

            if "ERASE DID/PDR SUCCESS" in response:

                self.ab_console.append(
                    "\n[DID ERASED SUCCESSFULLY]\n"
                )

            else:

                self.ab_console.append(
                    "\n[DID ERASE FAILED]\n"
                )

        #
        # Power OFF AB
        #
        if self.ab_adapter.is_connected():

            self.ab_console.append(
                "\n[POWER OFF AB]\n"
            )

            response = (
                self.ab_adapter.execute_command(
                    "websocket_test.sh powerswitch 0"
                )
            )

            if response:

                self.ab_console.append(
                    response
                )

        #
        # Power OFF CB
        #
        if self.cb_adapter.is_connected():

            self.cb_console.append(
                "\n[POWER OFF CB]\n"
            )

            response = (
                self.cb_adapter.execute_command(
                    "websocket_test.sh powerswitch 0"
                )
            )

            if response:

                self.cb_console.append(
                    response
                )

        #
        # Disconnect adapters
        #
        if self.ab_adapter.is_connected():

            self.ab_adapter.disconnect()

        if self.cb_adapter.is_connected():

            self.cb_adapter.disconnect()

        #
        # Update UI
        #
        self.lbl_cb_status.setText(
            "STATUS: DISCONNECTED"
        )

        self.lbl_cb_status.setStyleSheet("""
            color: #404040;
            font-weight: 600;
        """)

        self.lbl_ab_status.setText(
            "STATUS: DISCONNECTED"
        )

        self.lbl_ab_status.setStyleSheet("""
            color: #404040;
            font-weight: 600;
        """)

        self.cb_console.append(
            "\n[CB DISCONNECTED]\n"
        )

        self.ab_console.append(
            "\n[AB DISCONNECTED]\n"
        )

    # ============================================================
    # POWER OFF CB
    # ============================================================

    def power_off_cb(self):

        if not self.cb_adapter.is_connected():

            self.cb_console.append(
                "\n[CB NOT CONNECTED]\n"
            )

            return

        self.cb_console.append(
            "\n[POWER OFF COMMAND SENT]\n"
        )

        response = (
            self.cb_adapter.execute_command(
                "websocket_test.sh powerswitch 0"
            )
        )

        if response:

            self.cb_console.append(
                response
            )
    # ============================================================
    # CLEAR TERMINAL
    # ============================================================
    def clear_terminal(self):

        self.cb_console.clear()

        self.ab_console.clear()

        self.cb_log_buffer.clear()

        self.ab_log_buffer.clear()