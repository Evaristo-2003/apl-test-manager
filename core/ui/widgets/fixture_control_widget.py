from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QLineEdit
)
from PySide6.QtCore import Qt
from core.ui.widgets.status_indicator import StatusIndicator
from controllers.fixture_controller import FixtureController
from core.ui.styles import AppStyles
from PySide6.QtCore import (
    QThreadPool
)

from core.ui.workers.fixture_worker import (
    FixtureWorker
)
class FixtureControlWidget(QWidget):

    def __init__(
        self,
        fixture_controller,
        run_all_button=None,
        search_callback=None
    ):
        super().__init__()
        self.thread_pool = (
            QThreadPool.globalInstance()
        )
        layout = QVBoxLayout(self)

        self.fixture_status = StatusIndicator(
            "NOT CONNECTED"
        )

        self.fixture_controller = fixture_controller
        self.run_all_button = run_all_button
        self.search_callback = search_callback
        self.fixture_controller.register_indicator(
            self.fixture_status
        )
        self.fixture_controller.register_status_widget(
            self
        )
        group = QGroupBox(
            "Fixture Control"
        )

        group_layout = QGridLayout(group)

        self.btn_connect = QPushButton(
            "CONNECT"
        )
        self.fixture_controller.register_connect_button(
            self.btn_connect
        )
        self.btn_connect.clicked.connect(
            self.connect_fixture
        )






        self.btn_connect.setCursor(
            Qt.PointingHandCursor
        )




        group_layout.addWidget(
            self.btn_connect,
            0,
            0
        )



        if self.run_all_button:

            group_layout.addWidget(
                self.run_all_button,
                0,
                1
            )
        self.fixture_status.setMinimumWidth(
            180
        )

        self.fixture_status.setFixedHeight(
            35
        )
        self.search_box = QLineEdit()

        self.search_box.setPlaceholderText(
            "Search test..."
        )

        self.search_box.setFixedWidth(
            220
        )

        self.search_box.setStyleSheet("""
        QLineEdit {

            background: white;

            border: 1px solid #D0D0D0;

            border-radius: 0px;

            padding: 4px 8px;
        }
        """)

        if self.search_callback:

            self.search_box.textChanged.connect(
                self.search_callback
            )

        group_layout.addWidget(
            self.search_box,
            0,
            2
        )
#        group_layout.addWidget(
 #           self.fixture_status,
  #          0,
   #         3
    #    )
        self.btn_connect.setEnabled(False)
        layout.addWidget(group)
        self.set_fixture_status(
            "NOT CONNECTED"
        )
    def connect_fixture(self):

        status = (
            self.fixture_status.current_status
        )

        #
        # Si ya está conectado
        #
        if status == "READY":

            worker = FixtureWorker(
                self.fixture_controller
                .disconnect_fixture
            )

            self.thread_pool.start(
                worker
            )

            return

        #
        # Conectar
        #
        try:

            worker = FixtureWorker(
                self.fixture_controller
                .auto_connect_fixture
            )

            self.thread_pool.start(
                worker
            )

        except Exception:

            raise


    def set_fixture_status(
        self,
        status: str
    ):

        if status == "NOT CONNECTED":

            self.btn_connect.setText(
                "CONNECT"
            )

            self.btn_connect.setStyleSheet(
                AppStyles.FIXTURE_BUTTON_NOT_CONNECTED
            )

        elif status == "CONNECTING":

            self.btn_connect.setEnabled(
                False
            )

            self.btn_connect.setText(
                "CONNECTING..."
            )

            self.btn_connect.setStyleSheet(
                AppStyles.FIXTURE_BUTTON_CONNECTING
            )

        elif status == "READY":

            self.btn_connect.setEnabled(
                True
            )

            self.btn_connect.setText(
                "CONNECTED"
            )

            self.btn_connect.setStyleSheet(
                AppStyles.FIXTURE_BUTTON_READY
            )

        elif status == "FAILED":

            self.btn_connect.setEnabled(
                True
            )

            self.btn_connect.setText(
                "CONNECTION FAILED"
            )

            self.btn_connect.setStyleSheet(
                AppStyles.FIXTURE_BUTTON_FAILED
            )

        elif status == "DISCONNECTING":

            self.btn_connect.setEnabled(
                False
            )

            self.btn_connect.setText(
                "DISCONNECTING..."
            )

            self.btn_connect.setStyleSheet(
                AppStyles.FIXTURE_BUTTON_CONNECTING
            )