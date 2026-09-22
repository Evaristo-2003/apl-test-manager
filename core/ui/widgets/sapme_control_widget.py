#!/usr/bin/env python3

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox
)

from PySide6.QtCore import Qt


class SapmeControlWidget(QGroupBox):

    def __init__(
        self,
        load_callback,
        parent=None
    ):
        super().__init__(
            "SAPME CONTROL",
            parent
        )

        self.load_callback = load_callback

        self._build_ui()

    def _build_ui(self):

        layout = QVBoxLayout(self)

        #
        # SFC
        #

        sfc_layout = QHBoxLayout()

        sfc_layout.addWidget(
            QLabel("SFC:")
        )

        self.sfc_input = QLineEdit()

        self.sfc_input.setPlaceholderText(
            "Scan or enter SFC"
        )

        sfc_layout.addWidget(
            self.sfc_input
        )

        layout.addLayout(
            sfc_layout
        )

        #
        # Load button
        #

        self.btn_load = QPushButton(
            "LOAD SAPME"
        )

        self.btn_load.clicked.connect(
            self._load_clicked
        )

        layout.addWidget(
            self.btn_load
        )

        #
        # Status labels
        #

        self.lbl_status = QLabel(
            "🔴 NOT LOADED"
        )

        self.lbl_operation = QLabel(
            "Operation: ---"
        )

        self.lbl_tests = QLabel(
            "Tests Loaded: 0"
        )

        self.lbl_sync = QLabel(
            "Last Sync: ---"
        )

        layout.addWidget(
            self.lbl_status
        )

        layout.addWidget(
            self.lbl_operation
        )

        layout.addWidget(
            self.lbl_tests
        )

        layout.addWidget(
            self.lbl_sync
        )

    def _load_clicked(self):

        sfc = self.sfc_input.text().strip()

        if not sfc:
            return

        self.load_callback(sfc)

    def set_loading(self):

        self.lbl_status.setText(
            "🟡 LOADING"
        )

    def set_ready(
        self,
        operation,
        tests_loaded,
        sync_time
    ):

        self.lbl_status.setText(
            "🟢 READY"
        )

        self.lbl_operation.setText(
            f"Operation: {operation}"
        )

        self.lbl_tests.setText(
            f"Tests Loaded: {tests_loaded}"
        )

        self.lbl_sync.setText(
            f"Last Sync: {sync_time}"
        )

    def set_failed(self):

        self.lbl_status.setText(
            "🔴 FAILED"
        )