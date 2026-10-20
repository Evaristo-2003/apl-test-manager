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

        #
        # Export Button
        #
        self.btn_export = QPushButton(
            "EXPORT RESULTS"
        )
        self.btn_export.setStyleSheet("""
        QPushButton {

            background-color: #2D3748;
            color: white;

            border: none;
            border-radius: 0px;

            padding: 8px 16px;

            font-family: 'Segoe UI';
            font-size: 10pt;
            font-weight: 600;
        }

        QPushButton:hover {

            background-color: #4A5568;
        }

        QPushButton:pressed {

            background-color: #1A202C;
        }

        QPushButton:disabled {

            background-color: #B0B0B0;
            color: #E0E0E0;
        }
        """)
        layout.addWidget(
            self.btn_export
        )
        self.btn_export.setFixedWidth(
            180
        )
        button_layout = QHBoxLayout()

        button_layout.addStretch()
        button_layout.addWidget(
            self.btn_export
        )
        button_layout.addStretch()

        layout.addLayout(
            button_layout
        )
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