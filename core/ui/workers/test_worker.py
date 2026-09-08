#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Worker para ejecutar pruebas en hilos separados"""

from PySide6.QtCore import QRunnable, Signal, QObject, QThreadPool, Qt
from typing import Callable, Optional, Any
import traceback


class WorkerSignals(QObject):
    """Señales para comunicación entre hilos"""
    log = Signal(str)
    progress = Signal(int, int)
    finished = Signal(object)
    error = Signal(str)


class TestRunnable(QRunnable):
    """Runnable para ejecutar pruebas en hilo separado"""
    
    def __init__(self, func: Callable, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self._is_running = True
        self.setAutoDelete(True)
    
    def run(self):
        """Ejecuta la función en el hilo"""
        try:
            self.signals.log.emit("🚀 Hilo iniciado")
            result = self.func(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
            self.signals.log.emit("✅ Hilo finalizado")
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}\n{traceback.format_exc()}"
            try:
                self.signals.error.emit(error_msg)
                self.signals.log.emit(error_msg)
            except RuntimeError:
                # Las señales ya fueron destruidas, ignorar
                pass
        finally:
            # Limpiar señales
            try:
                self.signals.deleteLater()
            except:
                pass
    
    def stop(self):
        """Detiene la ejecución (flag)"""
        self._is_running = False


def run_test_in_thread(func: Callable, *args, on_finished: Optional[Callable] = None,
                       on_log: Optional[Callable] = None, on_error: Optional[Callable] = None,
                       on_progress: Optional[Callable] = None) -> TestRunnable:
    """Ejecuta una función en un hilo separado"""
    runnable = TestRunnable(func, *args)
    
    # Conectar señales
    if on_finished:
        runnable.signals.finished.connect(on_finished)
    if on_log:
        runnable.signals.log.connect(on_log)
    if on_error:
        runnable.signals.error.connect(on_error)
    if on_progress:
        runnable.signals.progress.connect(on_progress)
    
    # Ejecutar en thread pool
    QThreadPool.globalInstance().start(runnable)
    
    return runnable