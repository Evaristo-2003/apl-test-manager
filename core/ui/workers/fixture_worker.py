from PySide6.QtCore import (
    QObject,
    QRunnable,
    Signal
)


class FixtureSignals(QObject):

    finished = Signal(bool)
    error = Signal(str)


class FixtureWorker(QRunnable):

    def __init__(
        self,
        task
    ):
        super().__init__()

        self.task = task

        self.signals = (
            FixtureSignals()
        )

    def run(self):

        try:

            self.task()

            self.signals.finished.emit(
                True
            )

        except Exception as e:

            self.signals.error.emit(
                str(e)
            )