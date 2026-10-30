from PySide6.QtWidgets import (
    QWidget,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QLineEdit,
    QHBoxLayout,
    QMessageBox
)
from PySide6.QtCore import Qt, QThreadPool, Signal
from core.ui.widgets.progress_bar_indicator import ProgressBarIndicator
from core.ui.widgets.status_indicator import StatusIndicator
from core.ui.styles import AppStyles
from core.ui.workers.fixture_worker import FixtureWorker
 
 
class FixtureControlWidget(QWidget):
    
    # 🔥 Señal para comunicar el hilo secundario con el hilo principal de la UI
    _status_signal = Signal(str)
 
    def __init__(
        self,
        fixture_controller,
        run_all_button=None,
        search_callback=None
    ):
        super().__init__()
        self.thread_pool = QThreadPool.globalInstance()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
 
        self.fixture_controller = fixture_controller
        self.run_all_button = run_all_button
        self.search_callback = search_callback
        self._active_worker = None
 
        # Conectar la señal al método que actualiza la UI (se ejecutará en el hilo principal)
        self._status_signal.connect(self._update_ui_status)
 
        # 1. INDICADOR OCULTO (Requerido por el FixtureController)
        self.fixture_status = StatusIndicator("NOT CONNECTED")
        self.fixture_status.setVisible(False)
        
        self.fixture_controller.register_indicator(self.fixture_status)
        self.fixture_controller.register_status_widget(self)
 
        group = QGroupBox("Fixture Control")
        group_layout = QHBoxLayout(group)
        group_layout.setContentsMargins(10, 20, 10, 10) 
        group_layout.setSpacing(10)
 
        # 2. BOTÓN CONNECT
        self.btn_connect = QPushButton("CONNECT")
        self.btn_connect.setFixedSize(140, 32)
        self.btn_connect.setStyleSheet(AppStyles.FIXTURE_BUTTON_NOT_CONNECTED)
        self.btn_connect.setCursor(Qt.PointingHandCursor)
        self.btn_connect.clicked.connect(self.connect_fixture)
        self.fixture_controller.register_connect_button(self.btn_connect)
 
        # 3. SPINNER CIRCULAR
        self.spinner = ProgressBarIndicator()
 
        # 4. BOTÓN RUN ALL
        if self.run_all_button:
            self.run_all_button.setFixedSize(120, 32)
 
        # 5. BUSCADOR
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search test...")
        self.search_box.setFixedSize(200, 32)
        self.search_box.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #D0D0D0;
                border-radius: 6px;
                padding: 4px 8px;
            }
        """)
        if self.search_callback:
            self.search_box.textChanged.connect(self.search_callback)
 
        # ===== AGREGAR A LA LÍNEA =====
        group_layout.addWidget(self.btn_connect)
        group_layout.addWidget(self.spinner)
        group_layout.addStretch()
        group_layout.addWidget(self.run_all_button if self.run_all_button else QWidget())
        group_layout.addWidget(self.search_box)
 
        self.btn_connect.setEnabled(False)
        layout.addWidget(group)
        
        # Inicializamos la UI
        self.set_fixture_status("NOT CONNECTED")
 
 
    def connect_fixture(self):
        # Evitar doble clic
        if self._active_worker is not None:
            return 
 
        # Determinar si conectamos o desconectamos según el texto del botón
        if self.btn_connect.text() in ["DISCONNECT", "CONNECTED"]:
            worker = FixtureWorker(self.fixture_controller.disconnect_fixture)
        else:
            worker = FixtureWorker(self.fixture_controller.auto_connect_fixture)
        
        # Conectar las señales del worker
        worker.signals.error.connect(self._on_worker_error)
        worker.signals.finished.connect(self._on_worker_finished)
        self._active_worker = worker
        
        self.thread_pool.start(worker)
 
 
    def _on_worker_error(self, error_msg):
        print(f"Error en fixture: {error_msg}")
        # El estado se actualizará a FAILED a través del controlador, pero por si acaso forzamos
        self._status_signal.emit("FAILED")
        self._active_worker = None
 
 
    def _on_worker_finished(self, success):
        self._active_worker = None
 
 
    def set_fixture_status(self, status: str):
        # Este método es llamado por el controlador desde OTRO HILO.
        # Emitimos la señal para que se procese de forma segura en el hilo principal.
        self._status_signal.emit(status)
 
 
    def _update_ui_status(self, status: str):
        self.fixture_status.set_status(status)
 
        if status == "CONNECTING":
            self.btn_connect.setEnabled(False)
            self.btn_connect.setText("CONNECTING...")
            self.btn_connect.setStyleSheet(AppStyles.FIXTURE_BUTTON_CONNECTING)
            self.spinner.start("#F59E0B")
            return
            
        if status == "DISCONNECTING":
            self.btn_connect.setEnabled(False)
            self.btn_connect.setText("DISCONNECTING...")
            self.btn_connect.setStyleSheet(AppStyles.FIXTURE_BUTTON_CONNECTING)
            self.spinner.start("#DC2626")
            return
 
        self.spinner.stop()
        self.btn_connect.setEnabled(True)
 
        if status == "NOT CONNECTED":
            self.btn_connect.setText("CONNECT")
            self.btn_connect.setStyleSheet(AppStyles.FIXTURE_BUTTON_NOT_CONNECTED)
 
        elif status == "READY":
            self.btn_connect.setText("DISCONNECT") 
            self.btn_connect.setStyleSheet(AppStyles.FIXTURE_BUTTON_READY)
 
        elif status == "FAILED":
            self.btn_connect.setText("CONNECTION FAILED") 
            self.btn_connect.setStyleSheet(AppStyles.FIXTURE_BUTTON_FAILED)
 