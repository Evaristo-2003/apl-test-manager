#!/usr/bin/env python3

from functools import partial

from PySide6.QtWidgets import QGridLayout, QGroupBox, QScrollArea, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from config import dashboard_groups
from config.dashboard_groups import DASHBOARD_GROUPS
from core.ui.widgets.collapsible_group import CollapsibleGroup
from core.ui.widgets.test_card import TestCard


class DashboardBuilder:

    @staticmethod
    def filter_cards(
        search_text,
        dashboard_cards,
        dashboard_groups
    ):

        search_text = (
            search_text
            .strip()
            .lower()
        )

        #
        # Sin filtro
        #
        if not search_text:

            for card in dashboard_cards.values():

                card.show()

            for group in dashboard_groups.values():

                group.show()

                group.content.hide()

                group._expanded = False

                group.refresh_title()

            return

        #
        # Agrupar coincidencias por grupo
        #
        visible_groups = set()

        for group_name, group in dashboard_groups.items():

            group_has_match = False

            content_widget = (
                group.content_layout.itemAt(0).widget()
            )

            grid = content_widget.layout()

            for row in range(grid.count()):

                item = grid.itemAt(row)

                if not item:

                    continue

                card = item.widget()

                if not card:

                    continue

                test_name = (
                    card.test_name
                    if hasattr(card, "test_name")
                    else card.text()
                )

                if search_text in test_name.lower():

                    card.show()

                    group_has_match = True

                else:

                    card.hide()

            if group_has_match:

                group.show()

                #
                # expandir grupo
                #
                if not group._expanded:

                    group.toggle()

                visible_groups.add(
                    group_name
                )

            else:

                group.hide()
    def build(run_callback,view_result_callback):

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
            content_widget.setStyleSheet("""
            QWidget {
                background-color: #F7F8FA;
                border: 1px solid #D8DCE3;
                border-radius: 8px;
            }
            """)
            grid.setContentsMargins(
                12,
                12,
                12,
                12
            )

            group_box.content_layout.addWidget(
                content_widget
            )

            if group_name == "USB - PCIE":

                positions = {
                    "PCIe number of port": (0, 0),
                    "PCIe Iperf Test": (1, 0),

                    "USB3_3 number of port": (0, 1),
                    "USB3_3 Iperf Test": (1, 1),

                    "USB3_2 number of port": (2, 1),
                    "USB3_2 Iperf Test": (3, 1),

                    "USB2 number of port": (0, 2),
                    "USB2 Iperf Test": (1, 2),

                    "USB3 to USB2": (0, 3),
                    "USB2 to USB3": (1, 3),
                }

                for test_name in tests:

                    row, col = positions[test_name]

                    card = TestCard(test_name)

                    card.clicked.connect(
                        partial(
                            run_callback,
                            test_name
                        )
                    )

                    card.rightClicked.connect(
                        view_result_callback
                    )

                    grid.addWidget(
                        card,
                        row,
                        col
                    )

                    dashboard_cards[test_name] = card

            else:

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

                    card.rightClicked.connect(
                        view_result_callback
                    )

                    grid.addWidget(
                        card,
                        row,
                        col
                    )

                    dashboard_cards[test_name] = card

            main_layout.addWidget(
                group_box
            )

        main_layout.addStretch()

        scroll.setWidget(container)

        return (
            scroll,
            dashboard_cards,
            dashboard_groups
        )