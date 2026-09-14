#!/usr/bin/env python3

from PySide6.QtWidgets import (
    QGroupBox,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from core.ui.styles import AppStyles
from core.ui.widgets.fixture_control_widget import (
    FixtureControlWidget
)

class RunnerView:

    @staticmethod
    def create(
        serial_service,
        button_repo,
        test_controller,
        log_callback,
        show_details_callback,
        run_selected_callback,
        run_all_callback
    ):

        tab = QWidget()
        layout = QVBoxLayout(tab)

        #
        # Fixture Control
        #
        fixture_widget = FixtureControlWidget(
            serial_service,
            log_callback
        )

        layout.addWidget(
            fixture_widget
        )

        #
        # Test List
        #
        tests_group = QGroupBox(
            "Tests"
        )

        tests_layout = QVBoxLayout(
            tests_group
        )

        test_list = QListWidget()

        for button in button_repo.get_all():

            test_list.addItem(
                button["label"]
            )

            test_controller.test_status[
                button["label"]
            ] = "NOT_RUN"

        test_list.itemClicked.connect(
            show_details_callback
        )

        tests_layout.addWidget(
            test_list
        )

        layout.addWidget(
            tests_group
        )

        #
        # Actions
        #

        btn_execute = QPushButton(
            "▶ RUN SELECTED TEST"
        )

        btn_execute.clicked.connect(
            run_selected_callback
        )

        btn_execute.setStyleSheet(
            AppStyles.RUN_TEST_BUTTON
        )

        layout.addWidget(
            btn_execute
        )

        btn_all = QPushButton(
            "▶ RUN ALL SEQUENCE"
        )

        btn_all.clicked.connect(
            run_all_callback
        )

        btn_all.setStyleSheet(
            AppStyles.RUN_ALL_BUTTON
        )

        layout.addWidget(
            btn_all
        )
        #
        # Results
        #
        results_group = QGroupBox(
            "Log / Results"
        )

        results_layout = QVBoxLayout(
            results_group
        )

        result_box = QTextEdit()

        result_box.setReadOnly(
            True
        )

        result_box.setFontFamily(
            "Courier New"
        )

        result_box.setFontPointSize(
            10
        )

        results_layout.addWidget(
            result_box
        )

        layout.addWidget(
            results_group
        )

        return (
            tab,
            fixture_widget,
            test_list,
            result_box
        )