#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplicación principal - APL Test Manager"""

import sys
import json
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QTextEdit, QPushButton,QTabWidget
)
from core.services.serial_service import SerialService
from core.services.test_service import TestService
from core.repositories.button_repository import ButtonRepository
from core.ui.styles import AppStyles
from core.ui.workers.test_worker import run_test_in_thread
from controllers.test_controller import TestController
from core.ui.dashboard_view import DashboardView
from core.ui.view.runner_view import RunnerView

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APL Test Manager v2.0")
        self.resize(1280, 800)
        
        # Inicializar servicios
        self.serial_service = SerialService()
        self.test_service = TestService(self.serial_service)
        self.button_repo = ButtonRepository()
        self.fixture_controller = None
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
        
        # Configurar UI
        self._setup_ui()
        self.setStyleSheet(AppStyles.MAIN)
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Tab 1: Test Runner
        runner_tab = self._create_runner_tab()
        tabs.addTab(runner_tab, "Test Runner")
        
        # Tab 2: Dashboard
        dashboard_tab = self._create_dashboard_tab()
        tabs.addTab(dashboard_tab, "Dashboard")
        
        # Tab 3: Resultados
        results_tab = self._create_results_tab()
        tabs.addTab(results_tab, "Resultados")
    
    def _create_runner_tab(self):

        (
            tab,
            self.fixture_widget,
            self.test_list,
            self.result_box
        ) = RunnerView.create(
            self.serial_service,
            self.button_repo,
            self.test_controller,
            self.log_message,
            self.show_test_details,
            self.start_selected_test,
            self.run_all_sequence
        )

        self.fixture_status = (
            self.fixture_widget.fixture_status
        )

        self.fixture_controller = (
            self.fixture_widget.fixture_controller
        )

        return tab

    def _create_dashboard_tab(self):

        (
            tab,
            self.dashboard_cards,
            self.dashboard_groups,
            self.dashboard_controller,
            self.dashboard_summary_label,
            self.dashboard_progress_bar,
            self.dashboard_fixture_widget
        ) = DashboardView.create(
            self.run_dashboard_test,
            self.test_controller,
            self.button_repo,
            self.log_message,
            self.serial_service
        )

        return tab

        return tab
    
    def _create_results_tab(self) -> QWidget:
        """Crea la pestaña de resultados"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        btn_export = QPushButton("📊 EXPORT RESULTS")
        btn_export.clicked.connect(self.export_results)
        layout.addWidget(btn_export)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFontFamily("Courier New")
        layout.addWidget(self.results_text)
        
        return tab
    
    # ===== ACCIONES =====
    
    def log_message(self, text: str):
        """Añade mensaje al log"""
        try:
            from PySide6.QtGui import QTextCursor
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.result_box.append(f"[{timestamp}] {text}")
            cursor = self.result_box.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.result_box.setTextCursor(cursor)
        except RuntimeError:
            # El objeto ya fue eliminado, ignorar
            pass
    
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

    def safe_log_message(self, text: str):
        """Versión segura de log_message"""
        try:
            if not hasattr(self, 'result_box') or self.result_box is None:
                return
            from PySide6.QtGui import QTextCursor
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.result_box.append(f"[{timestamp}] {text}")
            cursor = self.result_box.textCursor()
            if cursor:
                cursor.movePosition(QTextCursor.End)
                self.result_box.setTextCursor(cursor)
        except RuntimeError:
            # El objeto ya fue eliminado, ignorar
            pass
        except Exception:
            # Cualquier otro error, ignorar
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
    
   # def run_dashboard_test(self, test_name: str):
    def run_dashboard_test(self, test_name: str):
        if self.dashboard_controller:
            self.dashboard_controller.run_dashboard_test(
                test_name
            )
    
    def show_test_details(self, item):
        """Muestra detalles de una prueba"""
        test_name = item.text()
        button = self.button_repo.get_by_label(test_name)
        if button:
            self.result_box.append(f"\n📋 {test_name}")
            self.result_box.append(f"Action: {button.get('action', {})}")
    
    def export_results(self):
        """Exporta resultados a JSON"""
        from datetime import datetime
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'results': {k: v.to_dict() if hasattr(v, 'to_dict') else str(v) 
                       for k, v in self.test_controller.test_results.items()}
        }
        
        filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        self.log_message(f"✅ Resultados exportados a {filename}")
        
        # Mostrar en pestaña de resultados
        self.results_text.setText(json.dumps(data, indent=2, default=str))


def main():
    """Punto de entrada principal"""
    # Crear directorios necesarios
    Path("logs").mkdir(exist_ok=True)
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
