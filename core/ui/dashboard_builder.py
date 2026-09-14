#!/usr/bin/env python3

from functools import partial

from PySide6.QtWidgets import QGridLayout, QGroupBox, QScrollArea, QVBoxLayout, QWidget

from config import dashboard_groups
from config.dashboard_groups import DASHBOARD_GROUPS
from core.ui.widgets.collapsible_group import CollapsibleGroup
from core.ui.widgets.test_card import TestCard


class DashboardBuilder:

    @staticmethod
    def build(run_callback):

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        main_layout = QVBoxLayout(container)

        dashboard_cards = {}
        dashboard_groups = {}
        for group_name, tests in DASHBOARD_GROUPS.items():

            group_box = CollapsibleGroup(
                group_name
            )
            dashboard_groups[group_name] = group_box
            content_widget = QWidget()

            grid = QGridLayout(content_widget)

            group_box.content_layout.addWidget(
                content_widget
            )

            for idx, test_name in enumerate(tests):

                row = idx // 4
                col = idx % 4

                card = TestCard(test_name)

                card.clicked.connect(
                    partial(
                        run_callback,
                        test_name
                    )
                )

                grid.addWidget(
                    card,
                    row,
                    col
                )

                dashboard_cards[test_name] = card

            main_layout.addWidget(group_box)

        main_layout.addStretch()

        scroll.setWidget(container)

        return (
            scroll,
            dashboard_cards,
            dashboard_groups
        )