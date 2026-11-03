import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
 
class LedSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Diagnóstico AB")
        self.setFixedSize(480, 250) # Ventana más ancha para acomodar la imagen
        self.setStyleSheet("background-color: #F3F2F1; font-family: 'Segoe UI';")
        
        # Resultados
        self.led_d62 = None
        self.led_d65 = None
 
        main_layout = QVBoxLayout(self)
 
        # Título y mensaje
        title = QLabel("Se detectó un fallo en el arranque de la AB.")
        title.setStyleSheet("font-weight: bold; font-size: 12px; color: #323130;")
        main_layout.addWidget(title)
        
        info = QLabel("Selecciona el estado final de los LEDs según la referencia:")
        info.setStyleSheet("color: #605E5C; margin-bottom: 5px;")
        main_layout.addWidget(info)
 
        # =========================================================
        #  CONTENEDOR HORIZONTAL (Imagen a la izquierda, Tabla a la derecha)
        # =========================================================
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
 
        # 1. Imagen de referencia (Izquierda)
        self.image_label = QLabel()
        # Busca la imagen en la carpeta assets de tu proyecto
        image_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "leds_reference.png")
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            # Escalamos la imagen para que no haga la ventana gigante
            self.image_label.setPixmap(pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.image_label.setText("[Imagen no encontrada]\nVerifica assets/leds_reference.png")
            self.image_label.setStyleSheet("border: 1px dashed #ccc; padding: 10px; color: #999;")
        
        content_layout.addWidget(self.image_label)
 
        # 2. Mini Tabla de LEDs (Derecha)
        table_layout = QHBoxLayout()
        table_layout.setSpacing(10)
 
        # Columna D62
        col_d62 = QVBoxLayout()
        lbl_d62 = QLabel("D62")
        lbl_d62.setStyleSheet("font-weight: bold; color: #323130;")
        lbl_d62.setAlignment(Qt.AlignCenter)
        self.cb_d62_high = QCheckBox("HIGH")
        self.cb_d62_low = QCheckBox("LOW")
        col_d62.addWidget(lbl_d62)
        col_d62.addWidget(self.cb_d62_high)
        col_d62.addWidget(self.cb_d62_low)
        col_d62.addStretch() # Empuja los checkboxes hacia arriba
        table_layout.addLayout(col_d62)
 
        # Línea separadora vertical
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setStyleSheet("color: #D2D0CE;")
        table_layout.addWidget(line)
 
        # Columna D65
        col_d65 = QVBoxLayout()
        lbl_d65 = QLabel("D65")
        lbl_d65.setStyleSheet("font-weight: bold; color: #323130;")
        lbl_d65.setAlignment(Qt.AlignCenter)
        self.cb_d65_high = QCheckBox("HIGH")
        self.cb_d65_low = QCheckBox("LOW")
        col_d65.addWidget(lbl_d65)
        col_d65.addWidget(self.cb_d65_high)
        col_d65.addWidget(self.cb_d65_low)
        col_d65.addStretch()
        table_layout.addLayout(col_d65)
 
        content_layout.addLayout(table_layout)
        main_layout.addLayout(content_layout)
        
        main_layout.addSpacing(10)
 
        # Botón de Confirmar
        btn_confirm = QPushButton("Continuar")
        btn_confirm.setStyleSheet("""
            QPushButton {
                background-color: #2D3748; color: white; font-weight: bold; 
                padding: 8px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #4A5568; }
        """)
        btn_confirm.clicked.connect(self.accept)
        main_layout.addWidget(btn_confirm)
 
        # Lógica para que solo se pueda seleccionar un HIGH o LOW por LED
        self.cb_d62_high.toggled.connect(self._on_d62_toggled)
        self.cb_d62_low.toggled.connect(self._on_d62_toggled)
        self.cb_d65_high.toggled.connect(self._on_d65_toggled)
        self.cb_d65_low.toggled.connect(self._on_d65_toggled)
 
    def _on_d62_toggled(self):
        if self.cb_d62_high.isChecked():
            self.cb_d62_low.setChecked(False)
        elif self.cb_d62_low.isChecked():
            self.cb_d62_high.setChecked(False)
 
    def _on_d65_toggled(self):
        if self.cb_d65_high.isChecked():
            self.cb_d65_low.setChecked(False)
        elif self.cb_d65_low.isChecked():
            self.cb_d65_high.setChecked(False)
 
    def get_selection(self):
        """Retorna el estado de los LEDs seleccionados."""
        d62 = "HIGH" if self.cb_d62_high.isChecked() else "LOW" if self.cb_d62_low.isChecked() else "UNKNOWN"
        d65 = "HIGH" if self.cb_d65_high.isChecked() else "LOW" if self.cb_d65_low.isChecked() else "UNKNOWN"
        return d62, d65
 