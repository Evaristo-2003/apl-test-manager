class DashboardController:

    def __init__(
        self,
        dashboard_cards,
        dashboard_groups,
        test_controller,
        button_repo,
        log_callback,
        summary_label,
        progress_bar
    ):
        self.dashboard_cards = dashboard_cards
        self.dashboard_groups = dashboard_groups

        self.test_controller = test_controller
        self.button_repo = button_repo

        self.log = log_callback

        self.summary_label = summary_label
        self.progress_bar = progress_bar

    def update_dashboard(self):

        for test_name, card in self.dashboard_cards.items():

            status = self.test_controller.test_status.get(
                test_name,
                "NOT_RUN"
            )

            card.set_status(status)

        from config.dashboard_groups import (
            DASHBOARD_GROUPS
        )

        for group_name, tests in DASHBOARD_GROUPS.items():

            total = len(tests)

            passed = 0

            for test_name in tests:

                status = self.test_controller.test_status.get(
                    test_name,
                    "NOT_RUN"
                )

                if status == "PASS":
                    passed += 1

            group = self.dashboard_groups.get(
                group_name
            )

            if group:

                group.update_summary(
                    passed,
                    total
                )
        all_status = list(
            self.test_controller.test_status.values()
        )

        passed = sum(
            1
            for s in all_status
            if s == "PASS"
        )

        failed = sum(
            1
            for s in all_status
            if s == "FAIL"
        )

        not_run = sum(
            1
            for s in all_status
            if s == "NOT_RUN"
        )

        total = len(all_status)

        completed = passed + failed

        percentage = (
            int(completed * 100 / total)
            if total
            else 0
        )

        self.summary_label.setText(
            f"✅ PASS: {passed}    "
            f"❌ FAIL: {failed}    "
            f"⏳ NOT RUN: {not_run}"
        )

        self.progress_bar.setValue(
            percentage
        )
    def run_dashboard_test(self, test_name):

        self.log(
            f"Dashboard Test: {test_name}"
        )

        self.test_controller.start_test(
            test_name
        )