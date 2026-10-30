from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen
 
 
class ProgressBarIndicator(QWidget):
    """Spinner circular de carga (estilo iOS/Windows)"""
 
    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0
        self._is_running = False
        self._color = QColor("#F59E0B") # Naranja por defecto
        
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.setInterval(30) # Velocidad de giro
        
        # Tamaño fijo cuadrado para que sea un círculo perfecto
        self.setFixedSize(24, 24)
        self.setVisible(False)
 
    def start(self, color_hex: str = "#F59E0B"):
        self._color = QColor(color_hex)
        self._is_running = True
        self.setVisible(True)
        self._timer.start()
 
    def stop(self):
        self._is_running = False
        self._timer.stop()
        self.setVisible(False)
 
    def _animate(self):
        # Girar 10 grados cada 30ms
        self._angle = (self._angle - 10) % 360
        self.update()
 
    def paintEvent(self, event):
        if not self._is_running:
            return
 
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
 
        rect = QRectF(2, 2, self.width() - 4, self.height() - 4)
 
        # 1. Fondo del círculo (gris claro)
        bg_pen = QPen(QColor("#E5E7EB"))
        bg_pen.setWidth(3)
        bg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(bg_pen)
        painter.drawEllipse(rect)
 
        # 2. Arco de color girando
        color_pen = QPen(self._color)
        color_pen.setWidth(3)
        color_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(color_pen)
        
        # Dibujar un arco de 90 grados (el 25% del círculo)
        # Qt usa grados * 16 para dibujar arcos
        painter.drawArc(rect, self._angle * 16, 90 * 16)