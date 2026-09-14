from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QProgressBar
)
from core.ui.widgets.fixture_control_widget import (
    FixtureControlWidget
)
from core.ui.dashboard_builder import DashboardBuilder
from controllers.dashboard_controller import DashboardController


class DashboardView:

    @staticmethod
    def create(
        run_callback,
        test_controller,
        button_repo,
        log_callback,
        serial_service
    ):

        (
            dashboard_widget,
            dashboard_cards,
            dashboard_groups
        ) = DashboardBuilder.build(
            run_callback
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
            serial_service,
            log_callback
        )
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(100)
        progress_bar.setValue(0)

        # Contenedor principal
        container = QWidget()

        layout = QVBoxLayout(container)
        
        layout.addWidget(fixture_widget)
        layout.addWidget(summary_label)
        layout.addWidget(progress_bar)
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
            fixture_widget
        )
