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

from PySide6.QtGui import QPixmap

from core.ui.styles import AppStyles
from core.utils.resource_path import resource_path


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
        # MAIN ROW
        #
        sfc_layout = QHBoxLayout()
        sfc_layout.setSpacing(15)

        #
        # PANEL SFC
        #
        sfc_panel = QWidget()

        sfc_panel.setStyleSheet("""
        QWidget {
            background-color: #F8F8F8;
            border: 1px solid #D0D0D0;
            border-radius: 6px;
        }
        """)

        sfc_panel.setFixedWidth(460)

        sfc_panel_layout = QHBoxLayout(
            sfc_panel
        )

        lbl_sfc = QLabel("SFC:")

        lbl_sfc.setStyleSheet("""
            font-family: 'Segoe UI';
            font-size: 10pt;
            font-weight: 600;
            border: none;
        """)

        sfc_panel_layout.addWidget(
            lbl_sfc
        )

        #
        # SFC INPUT
        #
        self.sfc_input = QLineEdit()
        self.sfc_input.setFixedHeight(32)
        self.sfc_input.setPlaceholderText(
            "Scan or enter SFC"
        )

        self.sfc_input.setFixedWidth(
            260
        )

        self.sfc_input.setStyleSheet("""
        QLineEdit {
            background: white;
            border: 2px solid #2D3748;
            border-radius: 0px;
            padding: 4px 8px;
            font-family: 'Segoe UI';
            font-size: 10pt;
            font-weight: 600;
        }

        QLineEdit:focus {
            border: 2px solid #3182CE;
        }
        """)

        sfc_panel_layout.addWidget(
            self.sfc_input
        )

        #
        # LOAD BUTTON
        #
        self.btn_load = QPushButton(
            "LOAD SAPME"
        )

        self.btn_load.setFixedWidth(130)
        self.btn_load.setFixedHeight(32)

        self.btn_load.setStyleSheet(
            AppStyles.RUN_ALL_BUTTON
        )

        self.btn_load.clicked.connect(
            self._load_clicked
        )

        sfc_panel_layout.addWidget(
            self.btn_load
        )

        sfc_layout.addWidget(
            sfc_panel
        )
#        sfc_layout.addStretch()
        #
        # PANEL STATUS
        #
        self.status_panel = QWidget()

        self.status_panel.setStyleSheet("""
        QWidget {
            background-color: #2D3748;
            border: 1px solid #44506A;
            border-radius: 0px;
        }
        """)

        self.status_panel.setFixedWidth(
            280
        )

        status_layout = QVBoxLayout(
            self.status_panel
        )
        status_layout.setAlignment(
            Qt.AlignCenter
        )
        status_layout.setContentsMargins(
            12,
            6,
            12,
            6
        )
        status_layout.setSpacing(
            2
        )
        self.lbl_ready = QLabel(
            "NOT LOADED"
        )
        self.lbl_ready.setFixedWidth(
            130
        )

        self.lbl_ready.setAlignment(
            Qt.AlignCenter
        )
        self.lbl_ready.setStyleSheet("""
        QLabel {
            background-color: #6B7280;
            color: white;
            border-radius: 0px;
            padding: 4px 10px;
            font-weight: 500;
        }
        """)

        self.lbl_info = QLabel(
            "-"
        )
        self.lbl_info.setAlignment(
            Qt.AlignCenter
        )
        self.lbl_info.setStyleSheet("""
        QLabel {

            color: #E2E8F0;

            border: none;

            font-family: 'Segoe UI';

            font-size: 9pt;

            font-weight: 600;
        }
        """)


        status_layout.addWidget(
            self.lbl_ready,
            alignment=Qt.AlignHCenter
        )

        status_layout.addWidget(
            self.lbl_info,
            alignment=Qt.AlignHCenter
        
        )


        sfc_layout.addWidget(
            self.status_panel
        )

        sfc_layout.addStretch()
        #
        # PANEL LOGO
        #
        self.project_widget = QWidget()

        self.project_widget.setFixedWidth(
            220
        )

        self.project_widget.setStyleSheet("""
        QWidget {
            background: transparent;
            border: none;
        }
        """)

        project_layout = QHBoxLayout(
            self.project_widget
        )

        project_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.lbl_project_logo = QLabel()

        self.lbl_project_logo.setFixedSize(
            200,
            70
        )

        self.lbl_project_logo.setAlignment(
            Qt.AlignCenter
        )

        project_layout.addWidget(
            self.lbl_project_logo
        )

        sfc_layout.addWidget(
            self.project_widget
        )

        layout.addLayout(
            sfc_layout
        )



    def _load_clicked(self):

        sfc = self.sfc_input.text().strip()

        if not sfc:
            return

        self.load_callback(
            sfc
        )

    def set_loading(self):

        self.lbl_ready.setText(
            "LOADING..."
        )

        self.lbl_ready.setStyleSheet("""
        QLabel {
            background-color: #F59E0B;
            color: white;
            border-radius: 0px;
            padding: 4px 10px;
            font-weight: 500;
        }
        """)

        self.lbl_info.setText("-")

        self.lbl_project_logo.clear()



    def set_ready(
        self,
        operation,
        tests_loaded,
        sync_time,
        project=""
    ):

        self.lbl_ready.setText(
            "READY"
        )

        self.lbl_ready.setStyleSheet("""
        QLabel {
            background-color: #16A34A;
            color: white;
            border-radius: 0px;
            padding: 4px 10px;
            font-weight: 500;
        }
        """)

        self.lbl_info.setText(
            f"{project.upper()}  •  {operation}"
        )


    def set_project(
        self,
        project
    ):

        self.lbl_project_logo.clear()

        logo_path = None

        if "STELLANTIS" in project:

            logo_path = resource_path(
                "assets/stellantis.png"
            )

        elif "GM" in project:

            logo_path = resource_path(
                "assets/gm.png"
            )
            print(
                f"Logo path: {logo_path}"
            )

        if logo_path:

            pixmap = QPixmap(
                str(logo_path)
            )

            if not pixmap.isNull():

                pixmap = pixmap.scaled(
                    190,
                    65,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )


                self.lbl_project_logo.setPixmap(
                    pixmap
                )


    def set_failed(self):

        self.lbl_ready.setText(
            "INVALID SFC"
        )

        self.lbl_ready.setStyleSheet("""
        QLabel {
            background-color: #DC2626;
            color: white;
            border-radius: 0px;
            padding: 4px 10px;
            font-weight: 500;
        }
        """)

        self.lbl_info.setText("-")

        self.lbl_project_logo.clear()
