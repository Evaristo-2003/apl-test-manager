from core.ui.workers.test_worker import run_test_in_thread
from PySide6.QtWidgets import QApplication

class TestController:

    def __init__(
        self,
        test_service,
        button_repo,
        log_callback,
        dashboard_callback,
        result_callback
    ):
        self.test_service = test_service
        self.button_repo = button_repo

        self.log = log_callback
        self.update_dashboard = dashboard_callback
        self.show_result = result_callback

        self.test_results = {}
        self.test_status = {}

    def start_test(self, test_name):

        button = self.button_repo.get_by_label(test_name)

        if not button:
            self.log(f"❌ Botón no encontrado: {test_name}")
            return

        self.test_status[test_name] = "RUNNING"
        self.update_dashboard()

        def execute():
            return self.test_service.execute_test(button)

        runnable = run_test_in_thread(
            execute,
            on_finished=self.on_test_finished,
            on_log=self.log,
            on_error=lambda e: self.log(f"❌ {e}")
        )

        self._current_runnable = runnable

    def on_test_finished(self, result):

        self.test_results[result.test_name] = result
        self.test_status[result.test_name] = result.status

        self.update_dashboard()
        self.show_result(result)

        if result.test_name == "All sequence":

            self.log("")
            self.log("=" * 70)
            self.log("📊 SECUENCIA COMPLETA FINALIZADA")
            self.log(f"Estado: {result.status}")

            for metric in result.metrics:
                self.log(
                    f"{metric.name}: {metric.value}"
                )

            self.log("=" * 70)

    def run_all_sequence(self):

        self.log("🚀 INICIANDO SECUENCIA COMPLETA")

        button = self.button_repo.get_by_label("All sequence")

        if not button:
            self.log("❌ Secuencia no encontrada")
            return

        run_test_in_thread(
            self.test_service.execute_test,
            button,
            on_finished=self.on_test_finished,
            on_log=self.log,
            on_error=lambda e: self.log(f"❌ {e}")
        )

    def run_dashboard_sequence(self):

        self.log(
            "🚀 INICIANDO DASHBOARD SEQUENCE"
        )

        return run_test_in_thread(
            self._dashboard_sequence_worker,
            on_log=self.log,
            on_error=lambda e: self.log(
                f"❌ {e}"
            )
        )

    from PySide6.QtWidgets import QApplication

    def _dashboard_sequence_worker(self):

        test_names = [
            name
            for name in self.button_repo.get_test_names()
            if name != "All sequence"
        ]

        for test_name in test_names:

            self.test_status[test_name] = "RUNNING"

            #self.update_dashboard()

           # QApplication.processEvents()

            button = self.button_repo.get_by_label(
                test_name
            )

            if not button:
                continue

            result = self.test_service.execute_test(
                button
            )

            self.test_results[
                test_name
            ] = result

            self.test_status[
                test_name
            ] = result.status

          #  self.update_dashboard()

           # QApplication.processEvents()

        return "DONE"
