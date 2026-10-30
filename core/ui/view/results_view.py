#!/usr/bin/env python3

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QRadioButton,
    QTextBrowser
)
from PySide6.QtCore import Qt
from core.ui.styles import AppStyles
 

class ResultsView(QWidget):

    def __init__(self):

        super().__init__()

        self.last_html = ""
        self.last_json = ""

        self._build_ui()

    def _build_ui(self):

        layout = QVBoxLayout(self)

        #
        # Export Section
        #
        export_label = QLabel(
            "Export formats"
        )

        layout.addWidget(
            export_label
        )

        export_layout = QHBoxLayout()

        self.chk_export_html = QCheckBox(
            "HTML"
        )

        self.chk_export_json = QCheckBox(
            "JSON"
        )

        self.chk_export_html.setChecked(
            True
        )

        self.chk_export_json.setChecked(
            True
        )

        export_layout.addWidget(
            self.chk_export_html
        )

        export_layout.addWidget(
            self.chk_export_json
        )

        export_layout.addStretch()

        layout.addLayout(
            export_layout
        )

        #
        # Preview Section
        #
        preview_label = QLabel(
            "Preview"
        )

        layout.addWidget(
            preview_label
        )

        preview_layout = QHBoxLayout()

        self.rb_show_html = QRadioButton(
            "HTML"
        )

        self.rb_show_json = QRadioButton(
            "JSON"
        )

        self.rb_show_html.setChecked(
            True
        )

        self.rb_show_html.toggled.connect(
            self.update_preview
        )

        self.rb_show_json.toggled.connect(
            self.update_preview
        )

        preview_layout.addWidget(
            self.rb_show_html
        )

        preview_layout.addWidget(
            self.rb_show_json
        )

        preview_layout.addStretch()

        layout.addLayout(
            preview_layout
        )

        # =====================================
        # EXPORT BUTTON
        # =====================================
        
        self.btn_export = QPushButton("EXPORT RESULTS")
        self.btn_export.setStyleSheet(AppStyles.EXPORT_RESULTS_BUTTON)
        self.btn_export.setFixedWidth(180)
        self.btn_export.setFixedHeight(36) # Altura fija para mantener simetría
        self.btn_export.setCursor(Qt.PointingHandCursor) # Manito al pasar el mouse
 
        # Layout para centrar el botón
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.btn_export)
        button_layout.addStretch()
 
        # Agregar al layout principal (no lo agregues suelto y luego en el HBox)
        layout.addLayout(button_layout)
 
        #
        # Preview Browser
        #
        self.browser = QTextBrowser()

        self.browser.setOpenExternalLinks(
            True
        )

        self.browser.setStyleSheet("""
        QTextBrowser {
            background: white;
            border: 1px solid #D0D0D0;
        }
        """)

        layout.addWidget(
            self.browser
        )

    def set_export_callback(
        self,
        callback
    ):

        self.btn_export.clicked.connect(
            callback
        )

    def set_html(
        self,
        html
    ):

        self.last_html = html

        self.update_preview()

    def set_json(
        self,
        json_text
    ):

        self.last_json = json_text

        self.update_preview()

    def update_preview(self):

        if self.rb_show_html.isChecked():

            self.browser.setHtml(
                self.last_html
            )

        else:

            self.browser.setPlainText(
                self.last_json
            )

    def export_html_enabled(
        self
    ):

        return (
            self.chk_export_html
            .isChecked()
        )

    def export_json_enabled(
        self
    ):

        return (
            self.chk_export_json
            .isChecked()
        )