from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QGroupBox,
    QPushButton,
    QVBoxLayout
)
from PySide6.QtCore import Qt
from core.ui.widgets.status_indicator import StatusIndicator
from controllers.fixture_controller import FixtureController
from core.ui.styles import AppStyles

class FixtureControlWidget(QWidget):

    def __init__(
        self,
        serial_service,
        log_callback
    ):
        super().__init__()

        layout = QVBoxLayout(self)

        self.fixture_status = StatusIndicator(
            "NOT CONNECTED"
        )

        self.fixture_controller = FixtureController(
            serial_service,
            log_callback,
            self.fixture_status
        )

        group = QGroupBox(
            "Fixture Control"
        )

        group_layout = QGridLayout(group)

        btn_connect = QPushButton(
            "CONNECT"
        )

        btn_connect.clicked.connect(
            self.fixture_controller.auto_connect_fixture
        )

        btn_disconnect = QPushButton(
            "DISCONNECT"
        )

        btn_disconnect.clicked.connect(
            self.fixture_controller.disconnect_fixture
        )

        btn_refresh = QPushButton(
            "REFRESH PORTS"
        )

        btn_refresh.clicked.connect(
            self.fixture_controller.refresh_ports
        )
        btn_connect.setStyleSheet(
            AppStyles.CONNECT_BUTTON
        )

        btn_disconnect.setStyleSheet(
            AppStyles.DISCONNECT_BUTTON
        )

        btn_refresh.setStyleSheet(
            AppStyles.REFRESH_BUTTON
        )

        btn_connect.setCursor(
            Qt.PointingHandCursor
        )

        btn_disconnect.setCursor(
            Qt.PointingHandCursor
        )

        btn_refresh.setCursor(
            Qt.PointingHandCursor
        )

        group_layout.addWidget(
            btn_connect,
            0,
            0
        )

        group_layout.addWidget(
            btn_disconnect,
            0,
            1
        )

        group_layout.addWidget(
            btn_refresh,
            0,
            2
        )

        group_layout.addWidget(
            self.fixture_status,
            0,
            3
        )

        layout.addWidget(group)