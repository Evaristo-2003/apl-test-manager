#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplicación principal - ATS (Automatic Test System)"""

import ctypes
import sys
import json
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QTextEdit, QPushButton,QTabWidget
)
from core.repositories.project_repository import ProjectRepository
from core.services.serial_service import SerialService
from core.services.test_service import TestService
from core.repositories.button_repository import ButtonRepository
from core.ui.styles import AppStyles
from core.ui.workers.test_worker import run_test_in_thread
from core.ui.app_icon import get_app_icon
from controllers.test_controller import TestController
from core.ui.dashboard_view import DashboardView
from core.ui.view.runner_view import RunnerView
from PySide6.QtCore import (Qt,QTimer)
from core.services.sapme_service import (
    SapmeService
)
from core.ui.widgets.sapme_control_widget import (
    SapmeControlWidget
)
from core.state.app_state import (
    app_state
)
from controllers.fixture_controller import (
    FixtureController
)
from core.reporting.html_report_builder import (
    HtmlReportBuilder
)
from core.ui.view.results_view import (
    ResultsView
)
from core.ui.view.analysis_view import (
    AnalysisView
)

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automatic Test System")
        self.resize(1280, 800)
        
        # Inicializar servicios
        self.setWindowIcon(get_app_icon())
        self.serial_service = SerialService()
        self.fixture_controller = FixtureController(
            self.serial_service,
            self.log_message
        )

        self.fixture_controller.analysis_callback = (
            self.on_analysis_failure
        )
        self.test_service = TestService(self.serial_service)
        self.sapme_service = SapmeService()
        self.button_repo = ButtonRepository()
        self.dashboard_controller = None       
        self.test_controller = TestController(
            self.test_service,
            self.button_repo,
            self.log_message,
            self.update_dashboard,
            self.show_test_result
        )

        # Configurar callbacks del servicio
        self.test_service.set_callbacks(
            on_progress=self.update_progress,
            on_log=self.log_message
        )
        
        # Estado
        self.uart_results = []
        self.gpio_results = []
        self.analysis_log = []
        # Configurar UI
        self.sapme_widget = SapmeControlWidget(
            self.load_sapme
        )

        self.tabs = QTabWidget()

        self.tabs.tabBar().setCursor(
            Qt.PointingHandCursor
        )

        self._setup_ui()
        self.dashboard_timer = QTimer()

        self.dashboard_timer.timeout.connect(
            self.dashboard_controller.update_dashboard
        )
        self.setStyleSheet(AppStyles.MAIN)
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        self.sapme_widget = SapmeControlWidget(
            self.load_sapme
        )

        main_layout.addWidget(
            self.sapme_widget
        )

        self.tabs = QTabWidget()

        self.tabs.tabBar().setCursor(
            Qt.PointingHandCursor
        )

        main_layout.addWidget(
            self.tabs
        )

#        # Tab 1
 #       runner_tab = self._create_runner_tab()
  #      self.tabs.addTab(
   #         runner_tab,
    #        "Test Runner"
     #   )

        # Tab 2
        dashboard_tab = self._create_dashboard_tab()
        self.tabs.addTab(
            dashboard_tab,
            "Dashboard"
        )

        # Tab 3
        results_tab = self._create_results_tab()
        self.tabs.addTab(
            results_tab,
            "Results"
        )
        # Tab 4
        analysis_tab = self._create_analysis_tab()

        self.tabs.addTab(
            analysis_tab,
            "Analysis"
        )
   
    def _create_dashboard_tab(self):

        (
            tab,
            self.dashboard_cards,
            self.dashboard_groups,
            self.dashboard_controller,
            self.dashboard_summary_label,
            self.dashboard_progress_bar,
            self.dashboard_fixture_widget,
            self.dashboard_run_all_button
        ) = DashboardView.create(
            self.run_dashboard_test,
            self.run_dashboard_sequence,
            self.open_dashboard_result,
            self.test_controller,
            self.button_repo,
            self.log_message,
            self.fixture_controller
        )

        return tab
    
    def _create_results_tab(self) -> QWidget:

        self.results_view = ResultsView()

        self.results_view.set_export_callback(
            self.export_results
        )

        return self.results_view
   
    def save_analysis_log(
        self,
        failure_type,
        analysis_steps=None
    ):

        Path(
            "analysis_logs"
        ).mkdir(
            exist_ok=True
        )

        filename = (
            f"analysis_logs/"
            f"{failure_type}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                "========================\n"
            )

            f.write(
                "CB LOG\n"
            )

            f.write(
                "========================\n\n"
            )

            f.write(
                self.fixture_controller
                .serial_service
                .get_cb_console_log()
            )

            f.write(
                "\n\n"
            )

            f.write(
                "========================\n"
            )

            f.write(
                "AB LOG\n"
            )

            f.write(
                "========================\n\n"
            )

            f.write(
                self.fixture_controller
                .serial_service
                .get_ab_console_log()
            )

        self.log_message(
            f"📄 Analysis log saved: {filename}"
        )

        return filename

    def on_analysis_failure(
        self,
        failure_type,
        analysis_steps
    ):

        self.save_analysis_log(
            failure_type,
            analysis_steps
        ) 
    # ===== ACCIONES =====

    def log_message(self, text: str):
        """Mensajes de log"""

        timestamp = (
            datetime.now()
            .strftime("%H:%M:%S")
        )

        print(
            f"[{timestamp}] {text}"
        )
        self.analysis_log.append(
            f"[{timestamp}] {text}"
        )
    def update_progress(self, current: int, total: int):
        """Actualiza progreso"""
        self.log_message(f"📊 Progreso: {current}/{total} ({current/total*100:.0f}%)")
    
    def update_dashboard(self):
        if self.dashboard_controller:
            self.dashboard_controller.update_dashboard()
    
    def start_selected_test(self):

        item = self.test_list.currentItem()

        if not item:
            self.log_message("⚠️ Selecciona una prueba")
            return

        self.test_controller.start_test(
            item.text()
        )

    def safe_log_message(
        self,
        text: str
    ):
        """Versión segura de log_message"""

        try:

            self.log_message(
                text
            )

        except Exception:

            pass

    def safe_error_handler(self, error_msg: str):
        """Maneja errores de forma segura"""
        self.safe_log_message(f"❌ {error_msg}")
    
#    def on_test_finished(self, result):
 #       """Callback cuando termina una prueba"""
  #      self.test_results[result.test_name] = result
   #     self.test_status[result.test_name] = result.status
        
    #    # Actualizar UI
    #    self.update_dashboard()
     #   self.show_test_result(result)
    
    def show_test_result(self, result):
        """Muestra el resultado de una prueba"""
        self.log_message("")
        self.log_message("=" * 70)
        status_icon = "✅" if result.status == "PASS" else "❌" if result.status == "FAIL" else "⏳"
        self.log_message(f"{status_icon} {result.test_name}")
        self.log_message(f"   Estado: {result.status}")
        self.log_message(f"   Duración: {result.duration_ms:.0f}ms")

        if result.metrics:
            self.log_message("   Métricas:")
            for metric in result.metrics:
                unit = f" {metric.unit}" if metric.unit else ""
                self.log_message(f"      • {metric.name}: {metric.value}{unit}")
        
        if result.verification:
            ver = result.verification
            self.log_message(f"   Verificación: {ver.get('status', 'UNKNOWN')}")
            if ver.get('message'):
                self.log_message(f"   Mensaje: {ver.get('message')}")
        
        self.log_message("=" * 70)
    
    def run_all_sequence(self):
        self.test_controller.run_all_sequence()

    def on_sequence_finished(self, result):
        """Callback cuando termina la secuencia completa"""
        self.log_message("")
        self.log_message("=" * 70)
        self.log_message("SECUENCIA COMPLETA FINALIZADA")
        self.log_message(f"   Estado: {result.status}")
        
        if result.metrics:
            for metric in result.metrics:
                self.log_message(f"   {metric.name}: {metric.value}")
        
        self.log_message("=" * 70)

    def run_dashboard_sequence(self):

        self.dashboard_run_all_button.setEnabled(
            False
        )

        self.dashboard_run_all_button.setText(
            "⏳ RUNNING..."
        )

        self.dashboard_timer.start(250)

        runnable = (
            self.test_controller.run_dashboard_sequence()
        )

        runnable.signals.finished.connect(
            lambda _: self.dashboard_sequence_finished()
        )
   # def run_dashboard_test(self, test_name: str):
    def run_dashboard_test(self, test_name: str):
        if self.dashboard_controller:
            self.dashboard_controller.run_dashboard_test(
                test_name
            )
    
    def show_test_details(self, item):
        """Muestra detalles de una prueba"""

        test_name = item.text()

        button = self.button_repo.get_by_label(
            test_name
        )

        if button:

            self.log_message(
                f"📋 {test_name}"
            )

            self.log_message(
                f"Action: {button.get('action', {})}"
            )
    
    def export_results(self):
        """Exporta resultados a JSON"""
        from datetime import datetime
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'results': {k: v.to_dict() if hasattr(v, 'to_dict') else str(v) 
                       for k, v in self.test_controller.test_results.items()}
        }
        json_text = json.dumps(
            data,
            indent=2,
            default=str
        )
        filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        if self.results_view.export_json_enabled():

            with open(
                filename,
                'w',
                encoding='utf-8'
            ) as f:

                json.dump(
                    data,
                    f,
                    indent=2,
                    default=str
                )

            self.log_message(
                f"✅ JSON exportado a {filename}"
            )
        html_filename = filename.replace(
            ".json",
            ".html"
        )

        html = HtmlReportBuilder.build(
            self.test_controller.test_results,
            sfc=getattr(
                app_state,
                "current_sfc",
                ""
            ),
            operation=getattr(
                app_state,
                "operation",
                ""
            ),
            project=getattr(
                app_state,
                "project",
                ""
            )
        )
        
        self.results_view.set_html(
            html
        )

        self.results_view.set_json(
            json_text
        )
        if self.results_view.export_html_enabled():

            with open(
                html_filename,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(html)

            self.log_message(
                f"✅ HTML exportado a {html_filename}"
            )      
        self.log_message(f"✅ Resultados exportados a {filename}")
        


    def dashboard_sequence_finished(self):

        self.dashboard_timer.stop()

        self.dashboard_controller.update_dashboard()

        self.dashboard_run_all_button.setEnabled(
            True
        )

        self.dashboard_run_all_button.setText(
            "RUN ALL TESTS"
        )

        self.log_message(
            "✅ DASHBOARD SEQUENCE FINALIZADA"
        )

    def open_dashboard_result(
        self,
        test_name
    ):

        result = (
            self.test_controller
            .test_results
            .get(test_name)
        )

        if not result:

            self.log_message(
                f"⚠️ No hay resultado para {test_name}"
            )

            return

        self.test_controller.show_result(
            result
        )

        self.tabs.setCurrentIndex(
            0
        )

    def load_sapme(
        self,
        sfc: str
    ):

        new_sfc = sfc.strip()

        source = (
            self.sapme_widget
            .get_source()
        )
        print(
            f"[SOURCE] {source}"
        )
        app_state.source = source

        previous_sfc = getattr(
            app_state,
            "current_sfc",
            None
        )

        print(
            f"LOAD SOURCE: {source}"
        )

        print(
            f"LOAD SFC: {new_sfc}"
        )

        #
        # Detectar cambio de SFC
        #
        sfc_changed = (
            previous_sfc is not None
            and
            previous_sfc != new_sfc
        )

        #
        # Si cambió el SFC
        #
        if sfc_changed:

            print(
                f"[NEW SFC] {previous_sfc} -> {new_sfc}"
            )

            self.reset_for_new_sfc()

        #
        # Mostrar estado visual
        #
        self.sapme_widget.set_loading()

        #
        # Cargar según origen
        #
        if source == "SAPME":

            success = (
                self.sapme_service
                .load_sfc(
                    new_sfc
                )
            )

        else:

            project_repo = ProjectRepository()

            app_state.current_sfc = new_sfc

            app_state.project = (
                project_repo.get_project_from_sfc(
                    new_sfc
                )
            )

            app_state.operation = "OP_FUNC_PCBA"

            app_state.sapme_ready = False

            app_state.tests_loaded = 0

            app_state.last_sync = datetime.now()

            success = True

        #
        # Resultado
        #
        if success:

            app_state.current_sfc = new_sfc

            self.sapme_widget.set_ready(
                operation=app_state.operation,
                tests_loaded=app_state.tests_loaded,
                sync_time=app_state.last_sync.strftime(
                    "%H:%M:%S"
                ),
                project=app_state.project
            )

            self.sapme_widget.set_project(
                app_state.project
            )

            self.fixture_controller.set_connect_enabled(
                True
            )

        else:

            self.sapme_widget.set_failed()

    def reset_for_new_sfc(self):

        print(
            "[RESET] Nueva corrida"
        )

        #
        # Limpiar resultados
        #
        self.test_controller.test_results.clear()

        self.test_controller.test_status.clear()
        for test_name in self.button_repo.get_test_names():

            self.test_controller.test_status[
                test_name
            ] = "NOT_RUN"
        #
        # Limpiar panel resultados
        #
        if hasattr(
            self,
            "results_view"
        ):

            self.results_view.set_html(
                ""
            )

            self.results_view.set_json(
                ""
            )
       
        #
        # Reiniciar flujo USB
        #
        self.test_controller.completed_tests.clear()

        self.test_controller.usb3_tests_completed = False

        self.test_controller.usb_mode = "USB3"

        #
        # Refrescar dashboard
        #
        self.update_dashboard()

    def _create_analysis_tab(self):

        self.analysis_view = AnalysisView(
            self.fixture_controller
        )

        self.analysis_view.btn_refresh_ports.clicked.connect(
            self.refresh_analysis_ports
        )

        self.refresh_analysis_ports()

        return self.analysis_view

    def refresh_analysis_ports(self):

        ports = (
            self.serial_service
            .get_ports()
        )

        self.analysis_view.set_ports(
            ports
        )

from PySide6.QtGui import (
    QColor,
    QPalette
)       

def main():
    """Punto de entrada principal"""
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "ATS.APLTestSystem.1.0"
    )
    # Crear directorios necesarios
    Path("logs").mkdir(
        exist_ok=True
    )

    app = QApplication(sys.argv)
    app.setWindowIcon(get_app_icon())

    #
    # Estilo uniforme
    #
    app.setStyle(
        "Fusion"
    )

    #
    # Force Light Theme
    #
    palette = QPalette()

    palette.setColor(
        QPalette.Window,
        QColor("#FFFFFF")
    )

    palette.setColor(
        QPalette.WindowText,
        QColor("#202020")
    )

    palette.setColor(
        QPalette.Base,
        QColor("#FFFFFF")
    )

    palette.setColor(
        QPalette.AlternateBase,
        QColor("#F5F5F5")
    )

    palette.setColor(
        QPalette.Text,
        QColor("#202020")
    )

    palette.setColor(
        QPalette.Button,
        QColor("#F0F0F0")
    )

    palette.setColor(
        QPalette.ButtonText,
        QColor("#202020")
    )

    app.setPalette(
        palette
    )

    #
    # Estilos globales
    #
    app.setStyleSheet("""
    QMainWindow {
        background-color: white;
    }

    QWidget {
        background-color: white;
        color: #202020;
    }

    QGroupBox {
        background-color: white;
        color: #202020;
    }

    QLabel {
        color: #202020;
    }
    """)

    window = MainWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
