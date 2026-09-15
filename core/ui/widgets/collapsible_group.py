from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton
)
from PySide6.QtCore import Qt

class CollapsibleGroup(QWidget):

    def __init__(self, title: str):
        super().__init__()

        self._title = title
        self._expanded = True
        self._summary = ""
        self.main_layout = QVBoxLayout(self)

        self.btn_toggle = QPushButton(
            f"▼ {title}"
        )

        self.btn_toggle.setCursor(
            Qt.PointingHandCursor
        )

        self.btn_toggle.clicked.connect(
            self.toggle
        )

        from core.ui.styles import AppStyles

        self.btn_toggle.setStyleSheet(
            AppStyles.GROUP_HEADER
        )

        self.main_layout.addWidget(
            self.btn_toggle
        )

        self.content = QWidget()

        self.content_layout = QVBoxLayout(
            self.content
        )

        # Iniciar cerrado
        self._expanded = False

        self.content.hide()

        self.btn_toggle.setText(
            f"▶ {self._title}"
        )

        self.main_layout.addWidget(
            self.content
        )

    def toggle(self):

        self._expanded = not self._expanded

        self.content.setVisible(
            self._expanded
        )

        self.refresh_title()

    def update_summary(
        self,
        passed: int,
        total: int
    ):

        self._summary = (
            f"({passed}/{total} PASS)"
        )

        self.refresh_title()

    def refresh_title(self):

        icon = (
            "▼"
            if self._expanded
            else "▶"
        )

        self.btn_toggle.setText(
            f"{icon} {self._title} {self._summary}"
        )