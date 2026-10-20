#!/usr/bin/env python3

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QTextBrowser,
    QGroupBox
)
from core.adapters.serial_adapter import (
    SerialAdapter
)
from PySide6.QtCore import Qt

from core.ui.styles import AppStyles
import threading
import time
class AnalysisView(QWidget):

    def __init__(self):

        super().__init__()
        self.cb_adapter = SerialAdapter()
        self.ab_adapter = SerialAdapter()
        self.cb_capture_running = False
        self.ab_capture_running = False
        self._build_ui()
        self.ab_log_buffer = []
        self.cb_log_buffer = []
    def _build_ui(self):

        layout = QVBoxLayout(self)


        #
        # ANALYSIS ACTIONS
        #
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

        self.btn_save_log = QPushButton(
            "SAVE LOG"
        )

        self.btn_save_log.setStyleSheet(
            AppStyles.RUN_ALL_BUTTON
        )

        self.btn_save_log.setFixedHeight(
            28
        )

        actions_layout.addStretch()

        actions_layout.addWidget(
            self.btn_refresh_ports
        )

        actions_layout.addWidget(
            self.btn_ab_connection
        )

        actions_layout.addWidget(
            self.btn_save_log
        )

        actions_layout.addStretch()

        layout.addLayout(
            actions_layout
        )
        #
        # CB BOARD
        #
        self.cb_group = QGroupBox(
            "CB BOARD"
        )

        cb_layout = QVBoxLayout(
            self.cb_group
        )
        cb_layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        cb_layout.setSpacing(
            6
        )
        self.lbl_cb_status = QLabel(
            "STATUS: DISCONNECTED"
        )

        self.lbl_cb_status.setStyleSheet("""
            font-weight: bold;
            color: #404040;
        """)

        cb_layout.addWidget(
            self.lbl_cb_status
        )

        cb_top = QHBoxLayout()

        cb_top.addWidget(
            QLabel("COM:")
        )

        self.cb_combo = QComboBox()

        self.cb_combo.setMinimumWidth(
            200
        )

        cb_top.addWidget(
            self.cb_combo
        )

        self.btn_cb_connect = QPushButton(
            "CONNECT"
        )

        self.btn_cb_connect.setStyleSheet(
            AppStyles.ANALYSIS_BUTTON
        )

        cb_top.addWidget(
            self.btn_cb_connect
        )

        self.btn_cb_kill = QPushButton(
            "KILL WSSC"
        )

        self.btn_cb_kill.setStyleSheet(
            AppStyles.ANALYSIS_BUTTON
        )

        cb_top.addWidget(
            self.btn_cb_kill
        )

        cb_top.addStretch()

        cb_layout.addLayout(
            cb_top
        )

        self.cb_console = QTextBrowser()

        self.cb_console.setPlaceholderText(
            "CB console output..."
        )

        cb_layout.addWidget(
            self.cb_console
        )

        layout.addWidget(
            self.cb_group
        )

        #
        # AB BOARD
        #
        self.ab_group = QGroupBox(
            "AB BOARD"
        )

        ab_layout = QVBoxLayout(
            self.ab_group
        )
        ab_layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        ab_layout.setSpacing(
            6
        )
        self.lbl_ab_status = QLabel(
            "STATUS: DISCONNECTED"
        )

        self.lbl_ab_status.setStyleSheet("""
            font-weight: bold;
            color: #404040;
        """)

        ab_layout.addWidget(
            self.lbl_ab_status
        )

        ab_top = QHBoxLayout()

        ab_top.addWidget(
            QLabel("COM:")
        )

        self.ab_combo = QComboBox()

        self.ab_combo.setMinimumWidth(
            200
        )

        ab_top.addWidget(
            self.ab_combo
        )

        self.btn_ab_connect = QPushButton(
            "CONNECT"
        )

        self.btn_ab_connect.setStyleSheet(
            AppStyles.ANALYSIS_BUTTON
        )

        ab_top.addWidget(
            self.btn_ab_connect
        )

        self.btn_ab_kill = QPushButton(
            "KILL WSSC"
        )

        self.btn_ab_kill.setStyleSheet(
            AppStyles.ANALYSIS_BUTTON
        )

        ab_top.addWidget(
            self.btn_ab_kill
        )

        ab_top.addStretch()

        ab_layout.addLayout(
            ab_top
        )

        self.ab_console = QTextBrowser()

        self.ab_console.setPlaceholderText(
            "AB console output..."
        )

        ab_layout.addWidget(
            self.ab_console
        )

        layout.addWidget(
            self.ab_group
        )

        layout.addStretch()
        self.btn_cb_connect.clicked.connect(
            self.connect_cb
        )

        self.btn_ab_connect.clicked.connect(
            self.connect_ab
        )

        self.btn_cb_kill.clicked.connect(
            self.kill_cb_wssc
        )

        self.btn_ab_kill.clicked.connect(
            self.kill_ab_wssc
        )
        self.btn_ab_connection.clicked.connect(
            self.start_ab_connection_analysis
        )
    def set_ports(
        self,
        ports
    ):

        self.cb_combo.clear()
        self.ab_combo.clear()

        self.cb_combo.addItems(
            ports
        )

        self.ab_combo.addItems(
            ports
        )

    def connect_cb(self):

        if self.cb_adapter.is_connected():

            self.cb_console.append(
                f"Already connected to {self.cb_adapter.port}"
            )

            return

        port = self.cb_combo.currentText()

        if not port:

            return


        ok = self.cb_adapter.connect(
            port
        )

        if ok:

            self.lbl_cb_status.setText(
                "STATUS: CONNECTED"
            )

            self.lbl_cb_status.setStyleSheet("""
                color: #16A34A;
                font-weight: 600;
            """)

            self.cb_console.append(
                f"Connected to {port}"
            )

            self.start_cb_capture()

        else:

            self.lbl_cb_status.setText(
                "STATUS: FAILED"
            )

            self.lbl_cb_status.setStyleSheet("""
                color: #DC2626;
                font-weight: 600;
            """)

            self.cb_console.append(
                f"Failed to connect to {port}"
            )
    def connect_ab(self):

        if self.ab_adapter.is_connected():

            self.ab_console.append(
                f"Already connected to {self.ab_adapter.port}"
            )

            return

        port = self.ab_combo.currentText()

        if not port:

            return

        ok = self.ab_adapter.connect(
            port
        )

        if ok:

            self.lbl_ab_status.setText(
                "STATUS: CONNECTED"
            )

            self.lbl_ab_status.setStyleSheet("""
                color: #16A34A;
                font-weight: 600;
            """)

            self.ab_console.append(
                f"Connected to {port}"
            )

            self.start_ab_capture()

        else:

            self.lbl_ab_status.setText(
                "STATUS: FAILED"
            )

            self.lbl_ab_status.setStyleSheet("""
                color: #DC2626;
                font-weight: 600;
            """)

            self.ab_console.append(
                f"Failed to connect to {port}"
            )
    def kill_cb_wssc(self):

        if not self.cb_adapter.is_connected():

            return

        response = (
            self.cb_adapter.execute_command(
                "hotkey_wssc.sh 0"
            )
        )

        self.cb_console.append(
            response
        )

    def kill_ab_wssc(self):

        if not self.ab_adapter.is_connected():

            return

        response = (
            self.ab_adapter.execute_command(
                "hotkey_wssc.sh 0"
            )
        )

        self.ab_console.append(
            response
        )

    def start_ab_connection_analysis(self):

        if not self.cb_adapter.is_connected():

            self.cb_console.append(
                "CB NOT CONNECTED"
            )

            return

        if not self.ab_adapter.is_connected():

            self.ab_console.append(
                "AB NOT CONNECTED"
            )

            return

        self.cb_log_buffer.clear()
        self.ab_log_buffer.clear()

        self.cb_console.clear()
        self.ab_console.clear()

        self.cb_console.append(
            "========== AB CONNECTION TEST =========="
        )

        self.ab_console.append(
            "========== AB CONNECTION TEST =========="
        )

        self.cb_adapter.send_command(
            "pwr_on_intl.sh 1"
        )

    def start_cb_capture(self):

        if self.cb_capture_running:

            return

        self.cb_capture_running = True

        def worker():

            while (
                self.cb_capture_running
                and
                self.cb_adapter.is_connected()
            ):

                try:

                    if self.cb_adapter._serial.in_waiting:

                        data = (
                            self.cb_adapter
                            ._serial
                            .read(
                                self.cb_adapter._serial.in_waiting
                            )
                            .decode(
                                "utf-8",
                                errors="ignore"
                            )
                        )

                        if data:

                            self.cb_log_buffer.append(
                                data
                            )

                            self.cb_console.insertPlainText(
                                data
                            )

                            self.cb_console.ensureCursorVisible()

                    time.sleep(0.01)

                except Exception:
                    break

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    def start_ab_capture(self):

        if self.ab_capture_running:

            return

        self.ab_capture_running = True

        def worker():

            while (
                self.ab_capture_running
                and
                self.ab_adapter.is_connected()
            ):

                try:

                    if self.ab_adapter._serial.in_waiting:

                        data = (
                            self.ab_adapter
                            ._serial
                            .read(
                                self.ab_adapter._serial.in_waiting
                            )
                            .decode(
                                "utf-8",
                                errors="ignore"
                            )
                        )

                        if data:

                            self.ab_log_buffer.append(
                                data
                            )

                            self.ab_console.insertPlainText(
                                data
                            )

                            self.ab_console.ensureCursorVisible()
                        if data:

                            self.ab_log_buffer.append(data)

                            print(
                                f"AB BUFFER SIZE: {len(self.ab_log_buffer)}"
                            )

                            self.ab_console.insertPlainText(data)
                    time.sleep(0.01)

                except Exception:
                    break

        threading.Thread(
            target=worker,
            daemon=True
        ).start()