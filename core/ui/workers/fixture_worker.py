from PySide6.QtCore import QObject, QRunnable, Signal
import traceback
 
class FixtureSignals(QObject):
    finished = Signal(bool)
    error = Signal(str)
    status = Signal(str)
 
class FixtureWorker(QRunnable):
    def __init__(self, task):
        super().__init__()
        self.task = task
        self.signals = FixtureSignals()
        self.setAutoDelete(False) 
 
    def run(self):
        try:
            self.task()
            self.signals.finished.emit(True)
        except Exception as e:
            # Imprime el error en la consola para que lo veas
            print(f"ERROR EN WORKER: {str(e)}\n{traceback.format_exc()}")
            self.signals.error.emit(str(e))
 