#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplicación principal - APL Test Manager"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from functools import partial
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QListWidget, QTextEdit, QPushButton, QGridLayout,
    QGroupBox, QLabel, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtCore import Qt, QThreadPool, Signal, QObject
from PySide6.QtGui import QTextCursor, QTextCursor  # ← Agregar esta línea
from core.services.serial_service import SerialService
from core.services.test_service import TestService
from core.repositories.button_repository import ButtonRepository
from core.repositories.limits_repository import LimitsRepository
from core.ui.widgets.test_card import TestCard
from core.ui.widgets.status_indicator import StatusIndicator
from core.ui.styles import AppStyles
from core.ui.workers.test_worker import run_test_in_thread


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
        
        # Configurar callbacks del servicio
        self.test_service.set_callbacks(
            on_progress=self.update_progress,
            on_log=self.log_message
        )
        
        # Estado
        self.test_results = {}
        self.test_status = {}
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
    
    def _create_runner_tab(self) -> QWidget:
        """Crea la pestaña de ejecución"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Fixture Control
        fixture_group = QGroupBox("Fixture Control")
        fixture_layout = QGridLayout(fixture_group)
        
        self.fixture_status = StatusIndicator("NOT CONNECTED")
        btn_connect = QPushButton("CONNECT")
        btn_connect.clicked.connect(self.auto_connect_fixture)
        btn_disconnect = QPushButton("DISCONNECT")
        btn_disconnect.clicked.connect(self.disconnect_fixture)
        btn_ports = QPushButton("REFRESH PORTS")
        btn_ports.clicked.connect(self.refresh_ports)
        
        fixture_layout.addWidget(btn_connect, 0, 0)
        fixture_layout.addWidget(btn_disconnect, 0, 1)
        fixture_layout.addWidget(btn_ports, 0, 2)
        fixture_layout.addWidget(self.fixture_status, 0, 3)
        layout.addWidget(fixture_group)
        
        # Test List
        tests_group = QGroupBox("Tests")
        tests_layout = QVBoxLayout(tests_group)
        
        self.test_list = QListWidget()
        for button in self.button_repo.get_all():
            self.test_list.addItem(button['label'])
            self.test_status[button['label']] = "NOT_RUN"
        
        self.test_list.itemClicked.connect(self.show_test_details)
        tests_layout.addWidget(self.test_list)
        layout.addWidget(tests_group)
        
        # Actions
        btn_execute = QPushButton("▶ RUN SELECTED TEST")
        btn_execute.clicked.connect(self.start_selected_test)
        btn_execute.setStyleSheet("background: #4CAF50; font-size: 14px; padding: 15px;")
        layout.addWidget(btn_execute)
        
        btn_all = QPushButton("▶ RUN ALL SEQUENCE")
        btn_all.clicked.connect(self.run_all_sequence)
        btn_all.setStyleSheet("background: #FF9800; font-size: 14px; padding: 15px;")
        layout.addWidget(btn_all)
        
        # Results
        results_group = QGroupBox("Log / Results")
        results_layout = QVBoxLayout(results_group)
        
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setFontFamily("Courier New")
        self.result_box.setFontPointSize(10)
        results_layout.addWidget(self.result_box)
        layout.addWidget(results_group)
        
        return tab
    
    from functools import partial  # ← Agregar al inicio del archivo

    def _create_dashboard_tab(self) -> QWidget:
        """Crea la pestaña de dashboard"""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        self.cards = {}
        test_names = self.button_repo.get_test_names()[:20]
        
        for idx, test_name in enumerate(test_names):
            row = idx // 4
            col = idx % 4
            
            card = TestCard(test_name)
            # ✅ CORREGIDO: usando partial
            card.clicked.connect(partial(self.run_dashboard_test, test_name))
            
            layout.addWidget(card, row, col)
            self.cards[test_name] = card
        
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
        """Actualiza el dashboard con los estados actuales"""
        for test_name, card in self.cards.items():
            status = self.test_status.get(test_name, "NOT_RUN")
            card.set_status(status)
    
    def refresh_ports(self):
        """Actualiza la lista de puertos disponibles"""
        ports = self.serial_service.get_ports()
        self.log_message(f"🔍 Puertos disponibles: {ports if ports else 'Ninguno'}")
    
    def start_selected_test(self):
        """Inicia la prueba seleccionada"""
        item = self.test_list.currentItem()
        if not item:
            self.log_message("⚠️ Selecciona una prueba")
            return
        
        test_name = item.text()
        button = self.button_repo.get_by_label(test_name)
        if not button:
            self.log_message(f"❌ Botón no encontrado: {test_name}")
            return
        
        # Actualizar estado visual
        self.test_status[test_name] = "RUNNING"
        self.update_dashboard()
        
        # ✅ Crear función de ejecución
        def execute_with_log():
            return self.test_service.execute_test(button)
        
        # ✅ Ejecutar con callbacks seguros
        runnable = run_test_in_thread(
            execute_with_log,
            on_finished=self.on_test_finished,
            on_log=self.safe_log_message,  # ← Usar función segura
            on_error=self.safe_error_handler
        )
        
        # ✅ Guardar referencia al runnable para evitar que se elimine
        self._current_runnable = runnable

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
    
    def on_test_finished(self, result):
        """Callback cuando termina una prueba"""
        self.test_results[result.test_name] = result
        self.test_status[result.test_name] = result.status
        
        # Actualizar UI
        self.update_dashboard()
        self.show_test_result(result)
    
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
        """Ejecuta la secuencia completa"""
        self.log_message("🚀 INICIANDO SECUENCIA COMPLETA")
        self.log_message("⚠️ Esto tomará varios minutos...")
        
        button = self.button_repo.get_by_label("All sequence")
        if not button:
            self.log_message("❌ Secuencia 'All sequence' no encontrada")
            return
        
        run_test_in_thread(
            self.test_service.execute_test,
            button,
            on_finished=self.on_sequence_finished,
            on_log=self.log_message,
            on_progress=self.update_progress,
            on_error=lambda e: self.log_message(f"❌ {e}")
        )
    
    def on_sequence_finished(self, result):
        """Callback cuando termina la secuencia completa"""
        self.log_message("")
        self.log_message("=" * 70)
        self.log_message("📊 SECUENCIA COMPLETA FINALIZADA")
        self.log_message(f"   Estado: {result.status}")
        
        if result.metrics:
            for metric in result.metrics:
                self.log_message(f"   {metric.name}: {metric.value}")
        
        self.log_message("=" * 70)
    
    def run_dashboard_test(self, test_name: str):
        """Ejecuta prueba desde dashboard"""
        self.log_message(f"🖱️ Click en: {test_name}")
        items = self.test_list.findItems(test_name, Qt.MatchFlag.MatchExactly)
        if items:
            self.test_list.setCurrentItem(items[0])
            self.start_selected_test()
    
    def show_test_details(self, item):
        """Muestra detalles de una prueba"""
        test_name = item.text()
        button = self.button_repo.get_by_label(test_name)
        if button:
            self.result_box.append(f"\n📋 {test_name}")
            self.result_box.append(f"Action: {button.get('action', {})}")
    
    def auto_connect_fixture(self):
        """Conecta automáticamente el fixture"""
        self.log_message("🔌 Conectando fixture...")
        self.fixture_status.set_status("CONNECTING")
        
        # Buscar CB
        self.log_message("📡 Buscando CB...")
        cb_port = self.serial_service.find_cb()
        if not cb_port:
            self.fixture_status.set_status("FAILED")
            self.log_message("❌ CB no encontrado")
            return
        
        self.log_message(f"✅ CB encontrado en {cb_port}")
        
        # Preparar CB
        self.log_message("⚙️ Preparando CB...")
        if not self.serial_service.prepare_cb():
            self.fixture_status.set_status("FAILED")
            self.log_message("❌ Error preparando CB")
            return
        self.log_message("✅ CB preparado")
        
        # Encender AB
        self.log_message("⏳ Encendiendo AB...")
        if not self.serial_service.power_on_ab():
            self.fixture_status.set_status("FAILED")
            self.log_message("❌ Error encendiendo AB")
            return
        self.log_message("✅ Comando de encendido enviado")
        
        # Buscar AB
        self.log_message("📡 Buscando AB (esto puede tomar hasta 60s)...")
        ab_port = self.serial_service.find_ab(timeout=60)
        if not ab_port:
            self.fixture_status.set_status("FAILED")
            self.log_message("❌ AB no encontrado")
            return
        
        self.log_message(f"✅ AB encontrado en {ab_port}")
        
        # Preparar AB
        self.log_message("⚙️ Preparando AB...")
        if not self.serial_service.prepare_ab():
            self.fixture_status.set_status("FAILED")
            self.log_message("❌ Error preparando AB")
            return
        self.log_message("✅ AB preparado")
        
        self.fixture_status.set_status("READY")
        self.log_message("🎯 FIXTURE LISTO")
    
    def disconnect_fixture(self):
        """Desconecta el fixture"""
        self.log_message("🔌 Desconectando fixture...")
        self.fixture_status.set_status("CONNECTING")
        
        # Borrar DID
        self.log_message("🧹 Borrando DID...")
        success, msg = self.serial_service.erase_did()
        self.log_message(f"   {msg}")
        
        # Apagar AB
        self.log_message("⏻ Apagando AB...")
        self.serial_service.power_off_ab()
        
        # Apagar CB
        self.log_message("⏻ Apagando CB...")
        self.serial_service.power_off_cb()
        
        # Desconectar
        self.log_message("🔌 Desconectando puertos...")
        self.serial_service.disconnect_all()
        
        self.fixture_status.set_status("NOT CONNECTED")
        self.log_message("✅ Fixture desconectado")
    
    def export_results(self):
        """Exporta resultados a JSON"""
        from datetime import datetime
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'results': {k: v.to_dict() if hasattr(v, 'to_dict') else str(v) 
                       for k, v in self.test_results.items()}
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
