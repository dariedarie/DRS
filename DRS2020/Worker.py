from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot


class Worker(QObject):
    finished = pyqtSignal()
    update = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.work)

    def start(self):
        self.thread.start()

    @pyqtSlot()
    def work(self):
        pass