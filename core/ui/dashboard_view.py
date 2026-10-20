from PySide6.QtWidgets import (
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel,
    QProgressBar
)
from config import dashboard_groups
from core.ui.styles import AppStyles
from core.ui.widgets.fixture_control_widget import (
    FixtureControlWidget
)
from core.ui.dashboard_builder import DashboardBuilder
from controllers.dashboard_controller import DashboardController
from PySide6.QtCore import Qt


class DashboardView:

    @staticmethod
    def create(
        run_callback,
        run_all_callback,
        view_result_callback,
        test_controller,
        button_repo,
        log_callback,
        fixture_controller
    ):

        (
            dashboard_widget,
            dashboard_cards,
            dashboard_groups
        ) = DashboardBuilder.build(
            run_callback,
            view_result_callback
        )
        run_all_button = QPushButton(
            "RUN ALL TESTS"
        )
        run_all_button.setStyleSheet(
            AppStyles.RUN_ALL_BUTTON
        )
        run_all_button.setCursor(
            Qt.PointingHandCursor
        )
        run_all_button.clicked.connect(
            run_all_callback
        )
        # Resumen
        summary_label = QLabel(
            "✅ PASS: 0    ❌ FAIL: 0    ⏳ NOT RUN: 0"
        )

        summary_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            padding: 6px;
        """)

        progress_bar = QProgressBar()
        fixture_widget = FixtureControlWidget(
            fixture_controller,
            run_all_button,
            lambda text: DashboardBuilder.filter_cards(
                text,
                dashboard_cards,
                dashboard_groups
            )
        )
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(100)
        progress_bar.setValue(0)

        # Contenedor principal
        container = QWidget()

        layout = QVBoxLayout(container)
        
        layout.addWidget(fixture_widget)
#        layout.addWidget(summary_label)
#        layout.addWidget(progress_bar)
        layout.addWidget(dashboard_widget)
      

        # Controller
        controller = DashboardController(
            dashboard_cards,
            dashboard_groups,
            test_controller,
            button_repo,
            log_callback,
            summary_label,
            progress_bar
        )

        # Inicializar contadores
        controller.update_dashboard()

        return (
            container,
            dashboard_cards,
            dashboard_groups,
            controller,
            summary_label,
            progress_bar,
            fixture_widget,
            run_all_button
        )
