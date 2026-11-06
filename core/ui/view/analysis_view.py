#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vista de Analysis - Captura continua de logs AB/CB"""

import os
import re
import time
import threading
from datetime import datetime

from PySide6.QtCore import QObject, QTimer, Signal, Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QTextBrowser,
    QGroupBox,
    QLineEdit,
)

from core.adapters.serial_adapter import SerialAdapter
from core.services.diagnostic_engine import DiagnosticEngine
from core.ui.styles import AppStyles
from core.ui.widgets.led_selector_dialog import LedSelectorDialog
from core.ui.workers.fixture_worker import FixtureWorker


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
        - Enviar comandos manuales a CB y AB
        - Guardar logs combinados
        - Ejecutar "AB CONNECTION" (power on AB)
    """

    def __init__(self, fixture_controller):
        super().__init__()

        # Inicializar controlador de fixture
        self.fixture_controller = fixture_controller

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
        self.signals.cb_text.connect(self._append_cb_text)
        self.signals.ab_text.connect(self._append_ab_text)

        self.refresh_ports()

    # ============================================================
    # CALLBACKS DE SEÑALES (UI Thread)
    # ============================================================

    def _append_cb_text(self, text: str):
        """Inserta texto en la consola CB y hace auto-scroll."""
        self.cb_console.moveCursor(QTextCursor.End)
        self.cb_console.insertPlainText(text)
        self.cb_console.moveCursor(QTextCursor.End)

    def _append_ab_text(self, text: str):
        """Inserta texto en la consola AB y hace auto-scroll."""
        self.ab_console.moveCursor(QTextCursor.End)
        self.ab_console.insertPlainText(text)
        self.ab_console.moveCursor(QTextCursor.End)

    # ============================================================
    # CONSTRUCCIÓN DE UI
    # ============================================================

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --------------------------
        # ANALYSIS ACTIONS
        # --------------------------
        actions_layout = QHBoxLayout()

        self.btn_refresh_ports = QPushButton("REFRESH PORTS")
        self.btn_refresh_ports.setStyleSheet(AppStyles.RUN_ALL_BUTTON)
        self.btn_refresh_ports.setFixedHeight(28)

        self.btn_ab_connection = QPushButton("AB CONNECTION")
        self.btn_ab_connection.setStyleSheet(AppStyles.RUN_ALL_BUTTON)
        self.btn_ab_connection.setFixedHeight(28)

        self.btn_clear_terminal = QPushButton("CLEAR TERMINAL")
        self.btn_clear_terminal.setStyleSheet(AppStyles.RUN_ALL_BUTTON)
        self.btn_clear_terminal.setFixedHeight(28)

        self.btn_save_log = QPushButton("SAVE LOG")
        self.btn_save_log.setStyleSheet(AppStyles.RUN_ALL_BUTTON)
        self.btn_save_log.setFixedHeight(28)

        self.btn_disconnect = QPushButton("DISCONNECT")
        self.btn_disconnect.setStyleSheet(AppStyles.RUN_ALL_BUTTON)
        self.btn_disconnect.setFixedHeight(28)

        actions_layout.addStretch()
        actions_layout.addWidget(self.btn_ab_connection)
        actions_layout.addWidget(self.btn_refresh_ports)
        actions_layout.addWidget(self.btn_clear_terminal)
        actions_layout.addWidget(self.btn_save_log)
        actions_layout.addWidget(self.btn_disconnect)

        layout.addLayout(actions_layout)

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

        # ============================================================
        # NUEVO: Barra de comandos para CB
        # ============================================================
        cb_cmd_layout = QHBoxLayout()
        cb_cmd_layout.addWidget(QLabel("Command:"))

        self.cb_command_input = QLineEdit()
        self.cb_command_input.setPlaceholderText("...")
        self.cb_command_input.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                padding: 4px 8px;
                font-family: Consolas;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 1px solid #3182CE;
            }
        """)
        self.cb_command_input.returnPressed.connect(self.send_cb_command)
        cb_cmd_layout.addWidget(self.cb_command_input)

        self.btn_cb_send = QPushButton("SEND")
        self.btn_cb_send.setStyleSheet(AppStyles.ANALYSIS_BUTTON)
        self.btn_cb_send.setFixedWidth(80)
        self.btn_cb_send.clicked.connect(self.send_cb_command)
        cb_cmd_layout.addWidget(self.btn_cb_send)

        cb_layout.addLayout(cb_cmd_layout)

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

        # ============================================================
        # NUEVO: Barra de comandos para AB
        # ============================================================
        ab_cmd_layout = QHBoxLayout()
        ab_cmd_layout.addWidget(QLabel("Command:"))

        self.ab_command_input = QLineEdit()
        self.ab_command_input.setPlaceholderText("...")
        self.ab_command_input.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                padding: 4px 8px;
                font-family: Consolas;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 1px solid #3182CE;
            }
        """)
        self.ab_command_input.returnPressed.connect(self.send_ab_command)
        ab_cmd_layout.addWidget(self.ab_command_input)

        self.btn_ab_send = QPushButton("SEND")
        self.btn_ab_send.setStyleSheet(AppStyles.ANALYSIS_BUTTON)
        self.btn_ab_send.setFixedWidth(80)
        self.btn_ab_send.clicked.connect(self.send_ab_command)
        ab_cmd_layout.addWidget(self.btn_ab_send)

        ab_layout.addLayout(ab_cmd_layout)

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
    # NUEVO: ENVIAR COMANDOS MANUALES
    # ============================================================

    def send_cb_command(self):
        """Envía un comando manual a la CB."""
        command = self.cb_command_input.text().strip()
        if not command:
            return

        if not self.cb_adapter.is_connected():
            self.cb_console.append("\n[ERROR] CB no está conectado.\n")
            return

        # Mostrar el comando en la consola
        self.cb_console.append(f"\n[TX] {command}")

        # Enviar el comando al adaptador
        self.cb_adapter.send_command(command)

        # Limpiar el input
        self.cb_command_input.clear()

    def send_ab_command(self):
        """Envía un comando manual a la AB."""
        command = self.ab_command_input.text().strip()
        if not command:
            return

        if not self.ab_adapter.is_connected():
            self.ab_console.append("\n[ERROR] AB no está conectado.\n")
            return

        # Mostrar el comando en la consola
        self.ab_console.append(f"\n[TX] {command}")

        # Enviar el comando al adaptador
        self.ab_adapter.send_command(command)

        # Limpiar el input
        self.ab_command_input.clear()

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
    # AB CONNECTION (Power On & Analyze)
    # ============================================================

    def start_ab_connection_analysis(self):
        """Ejecuta el flujo de AB CONNECTION y análisis en tiempo real."""

        if not self.cb_adapter.is_connected():
            self.cb_console.append("\n[ERROR] CB NOT CONNECTED\n")
            return

        if not self.ab_adapter.is_connected():
            self.ab_console.append("\n[ERROR] AB NOT CONNECTED\n")
            return

        self.cb_console.append("\n========== CB CONNECTION TEST ==========")
        self.ab_console.append("\n========== AB CONNECTION TEST ==========")

        self.cb_log_buffer.clear()
        self.ab_log_buffer.clear()
        self.cb_console.clear()
        self.ab_console.clear()

        self.cb_console.append("========== CB CONNECTION TEST ==========")
        self.ab_console.append("========== AB CONNECTION TEST ==========")

        self.cb_console.append("[CB] Enviando comando de encendido a la AB...")
        self.cb_adapter.send_command("pwr_on_intl.sh 1")

        self.cb_console.append("[DIAGNOSTIC] Monitoreando el arranque de la AB...")

        # Variables para el monitoreo en tiempo real
        self._diag_start_time = time.time()

        # Si ya había un timer corriendo, lo detenemos para que no se duplique
        if hasattr(self, '_diag_timer') and self._diag_timer.isActive():
            self._diag_timer.stop()

        self._diag_timer = QTimer(self)
        self._diag_timer.timeout.connect(self._check_ab_log_realtime)
        self._diag_timer.start(2000)  # Revisar cada 2 segundos

    # ============================================================
    # CHECK AB LOG REALTIME
    # ============================================================

    def _check_ab_log_realtime(self):
        """Revisa el log. Si no hay falla clara, pregunta por los LEDs."""
 
        # Usar el buffer completo en lugar del texto visible
        ab_log = "".join(self.ab_log_buffer)
        if not ab_log:
            ab_log = self.ab_console.toPlainText()
 
        tiempo_transcurrido = time.time() - self._diag_start_time
 
        # ============================================================
        # 1. Detección temprana del prompt de Linux -> PASS
        # ============================================================
        prompt_patterns = [
            r"root@harman-si-intel-plk",
            r"root@.*:~#",
            r"login:",
            r"init_connection",          # NUEVO: El sistema ya está en el prompt
            r"No route to host",          # NUEVO: El sistema ya está en el prompt
            r"Re-init conn",              # NUEVO: El sistema ya está en el prompt
        ]
        for pattern in prompt_patterns:
            if re.search(pattern, ab_log, re.IGNORECASE):
                self._diag_timer.stop()
                self._show_diagnostic_result({
                    "mode": "Falla FALSA",
                    "status": "PASS",
                    "diagnosis": "Arranque de la AB exitoso. Sistema de memoria y alimentación OK.",
                    "action": "Ninguna."
                })
                return
 
        # ============================================================
        # 2. Detección de fallas FATALES (irreversibles) -> Detener inmediatamente
        # ============================================================
        fallas_fatales = [
            r"EXCEPTION\s*#\d+",
            r"KERNEL PANIC",
            r"ACPI MEMORY OR I/O RESET_REG",
            r"MACHINE CHECK EXCEPTION",
            r"NO MEMORY DETECTED",
        ]
        for pattern in fallas_fatales:
            if re.search(pattern, ab_log, re.IGNORECASE):
                self._diag_timer.stop()
                result = DiagnosticEngine.analyze_ab_log_only(ab_log)
                self._show_diagnostic_result(result)
                return
 
        # ============================================================
        # 3. Si pasaron 35 segundos sin prompt ni falla fatal,
        #    analizamos el log (puede ser un caso ambiguo).
        #    Aumentamos a 35s porque el arranque de Linux puede tardar.
        # ============================================================
        if tiempo_transcurrido > 35:
            self._diag_timer.stop()
 
            if not ab_log.strip() or len(ab_log) < 50:
                self.cb_console.append("\n[DIAGNOSTIC]  No se recibió log de la AB en 35s.")
                self.cb_console.append("[DIAGNOSTIC] Solicitando estado de LEDs para diagnóstico...")
 
                dialog = LedSelectorDialog(self)
                if dialog.exec():
                    led_d62, led_d65 = dialog.get_selection()
                    result = DiagnosticEngine.analyze_with_leds(ab_log, led_d62, led_d65)
                    self._show_diagnostic_result(result)
                else:
                    self.cb_console.append("\n[DIAGNOSTIC] Diagnóstico cancelado por el operador.")
                return
 
            result = DiagnosticEngine.analyze_ab_log_only(ab_log)
 
            if result["status"] != "UNKNOWN":
                self._show_diagnostic_result(result)
                return
 
            self.cb_console.append("[DIAGNOSTIC] Log no concluyente. Solicitando estado de LEDs...")
            dialog = LedSelectorDialog(self)
            if dialog.exec():
                led_d62, led_d65 = dialog.get_selection()
                result = DiagnosticEngine.analyze_with_leds(ab_log, led_d62, led_d65)
                self._show_diagnostic_result(result)
            else:
                self.cb_console.append("\n[DIAGNOSTIC] Diagnóstico cancelado por el operador.")
 
 

    def _show_diagnostic_result(self, result):
        """Muestra el resultado final en la consola y en una ventana emergente simplificada."""

        # 1. Escribir en la consola de la CB
        self.cb_console.append("\n" + "="*50)
        self.cb_console.append(f"🏥 DIAGNÓSTICO AUTOMÁTICO")
        self.cb_console.append(f"Modo de Falla: {result['mode']}")
        self.cb_console.append(f"Error: {result['diagnosis']}")
        self.cb_console.append("="*50 + "\n")

        # 2. Mostrar la ventana emergente final
        msg_final = QMessageBox()

        if result['status'] == "FAIL":
            msg_final.setIcon(QMessageBox.Critical)
            msg_final.setWindowTitle("Falla Detectada")
        elif result['status'] == "PASS":
            msg_final.setIcon(QMessageBox.Information)
            msg_final.setWindowTitle("Prueba Exitosa")
        else:
            msg_final.setIcon(QMessageBox.Warning)
            msg_final.setWindowTitle("Resultado Desconocido")

        # Mostramos solo el Modo y el Error (sin sugerencias)
        msg_final.setText(f"<b>Modo de Falla:</b> {result['mode']}")

        if result['status'] == "PASS":
            msg_final.setInformativeText("Arranque correcto.")
        elif result['mode'] == "UNKNOWN":
            msg_final.setInformativeText("No se pudo identificar el error. Requiere análisis manual.")
        else:
            msg_final.setInformativeText(f"<b>Error:</b>\n{result['diagnosis']}")

        msg_final.exec()

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
    # DISCONNECT ALL (Solo cierra puertos y actualiza UI)
    # ============================================================
    def disconnect_all(self):

        # 1. Detener capturas
        self.cb_capture_running = False
        self.ab_capture_running = False

        # 2. Desconectar adaptadores
        if self.ab_adapter.is_connected():
            self.ab_adapter.disconnect()

        if self.cb_adapter.is_connected():
            self.cb_adapter.disconnect()

        # 3. Actualizar UI (Estado de los labels)
        self.lbl_cb_status.setText("STATUS: DISCONNECTED")
        self.lbl_cb_status.setStyleSheet("""
            color: #404040;
            font-weight: 600;
        """)

        self.lbl_ab_status.setText("STATUS: DISCONNECTED")
        self.lbl_ab_status.setStyleSheet("""
            color: #404040;
            font-weight: 600;
        """)

        # 4. Mensajes finales en consola
        self.cb_console.append("\n[CB DISCONNECTED]\n")
        self.ab_console.append("\n[AB DISCONNECTED]\n")

    # ============================================================
    # POWER OFF CB (Apagar placa y desconectar puertos)
    # ============================================================
    def power_off_cb(self):
        if not self.cb_adapter.is_connected():
            self.cb_console.append("\n[CB NOT CONNECTED]\n")
            return

        if not self.ab_adapter.is_connected():
            self.cb_console.append("\n[AB NOT CONNECTED, CANNOT ERASE DID]\n")
            return

        self.cb_console.append("\n[ERASE DID EN PROGRESO...]\n")
        self._power_off_response = ""

        def process_power_off():
            # 1. Mandar erase did a la AB y esperar el prompt de Linux
            erase_response = self.ab_adapter.execute_command_until(
                "websocket_test.sh erasedid",
                "root@harman-si-intel-plk:~#",  # Esperamos el prompt
                60
            )
            self._power_off_response = erase_response

            # 2. Mandar el power off a la CB inmediatamente después
            self.cb_adapter.execute_command(
                "websocket_test.sh powerswitch 0"
            )

        worker = FixtureWorker(process_power_off)

        def on_finished(success):
            # Si la AB respondió, lo mostramos
            if self._power_off_response:
                self.ab_console.append(self._power_off_response)

            self.cb_console.append("\n[ERASE DID FINALIZADO]\n")
            self.cb_console.append("\n[POWER OFF COMMAND SENT TO CB]\n")

            # Desconectar adaptadores y actualizar UI
            # 1. Detener capturas
            self.cb_capture_running = False
            self.ab_capture_running = False

            # 2. Desconectar adaptadores
            if self.ab_adapter.is_connected():
                self.ab_adapter.disconnect()

            if self.cb_adapter.is_connected():
                self.cb_adapter.disconnect()

            # 3. Actualizar UI (Estado de los labels)
            self.lbl_cb_status.setText("STATUS: DISCONNECTED")
            self.lbl_cb_status.setStyleSheet("""
                color: #404040;
                font-weight: 600;
            """)

            self.lbl_ab_status.setText("STATUS: DISCONNECTED")
            self.lbl_ab_status.setStyleSheet("""
                color: #404040;
                font-weight: 600;
            """)

            # 4. Mensajes finales en consola
            self.cb_console.append("\n[CB DISCONNECTED]\n")
            self.ab_console.append("\n[AB DISCONNECTED]\n")

        def on_error(error_msg):
            self.cb_console.append(f"\n[ERROR EN EL HILO]: {error_msg}\n")

        worker.signals.finished.connect(on_finished)
        worker.signals.error.connect(on_error)

        from PySide6.QtCore import QThreadPool
        QThreadPool.globalInstance().start(worker)

    # ============================================================
    # DIAGNOSTIC ENGINE
    # ============================================================
    def run_diagnostics(self):
        """Analiza el log actual de la AB y muestra el diagnóstico."""

        # 1. Obtener el texto actual de la consola de la AB
        ab_log = self.ab_console.toPlainText()

        if not ab_log.strip():
            self.cb_console.append("\n[DIAGNOSTIC] ⚠️ No hay log en la AB para analizar.\n")
            return

        # 2. Ejecutar el motor de reglas
        result = DiagnosticEngine.analyze_ab_log(ab_log)

        # 3. Mostrar el resultado en la consola de la CB (o en un QMessageBox)
        self.cb_console.append("\n" + "="*50)
        self.cb_console.append(f"🏥 DIAGNÓSTICO AUTOMÁTICO (Modo {result['mode']})")
        self.cb_console.append(f"Estado: {result['status']}")
        self.cb_console.append(f"🔍 Problema: {result['diagnosis']}")
        self.cb_console.append(f"🛠️ Acción: {result['action']}")
        self.cb_console.append("="*50 + "\n")

        # Opcional: Mostrar una ventana emergente si es FAIL
        if result['status'] == "FAIL":
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle(f"Falla Detectada - Modo {result['mode']}")
            msg.setText(f"Problema: {result['diagnosis']}")
            msg.setInformativeText(f"Acción Sugerida:\n{result['action']}")
            msg.exec()

    # ============================================================
    # CLEAR TERMINAL
    # ============================================================
    def clear_terminal(self):
        self.cb_console.clear()
        self.ab_console.clear()
        self.cb_log_buffer.clear()
        self.ab_log_buffer.clear()