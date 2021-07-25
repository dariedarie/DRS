from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QDesktopWidget, QComboBox, QMessageBox, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QCursor, QKeyEvent, QIcon
from PyQt5.QtCore import Qt
import sys

from GameMode import GameModeWindow


class MainWindow(QWidget):
    MainWindowH = 600
    MainWindowW = 800

    def __init__(self):  # Here we initialize MainWindow class
        super().__init__()  # Here we initialize base class (Super class)  i.e QWidget

        self.initUI()

    # noinspection PyMethodMayBeStatic
    def run(self):
        # print("Run Run")
        self.GameMode = GameModeWindow(self)
        self.hide()

    # Nice way to close application
    # noinspection PyMethodMayBeStatic
    def quitGame(self):
        QApplication.instance().exit()

    def initUI(self):
        pixmap = QPixmap("resources/topimage.jpg")
        pixmap2 = pixmap.scaledToWidth(600)

        lbl = QLabel(self)
        lbl.setPixmap(pixmap2)
        lbl.move(100, 10)
        lbl.setStyleSheet("border: 2px solid blue;")

        self.setWindowIcon(QIcon('resources/icon.png'))

        self.initMainMenuButtons()
        self.resize(self.MainWindowH, self.MainWindowW)
        self.setMinimumHeight(self.MainWindowH)
        self.setMinimumWidth(self.MainWindowW)
        self.setMaximumHeight(self.MainWindowH)
        self.setMaximumWidth(self.MainWindowW)
        self.setWindowTitle("Turn Snake - The first Snake turn based strategy")
        self.setStyleSheet("background-color: black;")

        self.center()
        self.show()

    def center(self):
        screen = QDesktopWidget().screenGeometry()  # Here we take our full screen geometry
        size = self.geometry()  # Here we take our app geometry
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    # In this method we will initialize our buttons, toolbars etc
    def initMainMenuButtons(self):
        self.startButton = QtWidgets.QPushButton("", self)
        self.startButton.setStyleSheet(
            "border:2px solid blue; color: " "blue;font-size: 27px; font-family: Calibri; "
            "background-image: url(resources/startbutton.jpg);")
        self.startButton.setGeometry(275, 440, 250, 50)
        self.startButton.setCursor(Qt.PointingHandCursor)
        self.startButton.released.connect(self.run)

        self.exitButton = QtWidgets.QPushButton("", self)
        self.exitButton.setCursor(Qt.PointingHandCursor)
        self.exitButton.setStyleSheet(
            "border:2px solid blue; color: " "blue;font-size: 27px; font-family: Calibri;"
            "background-image: url(resources/exitbutton.jpg);")
        self.exitButton.setGeometry(275, 500, 250, 50)
        self.exitButton.released.connect(self.quitGame)

    # Method below gets called every time we press some key on keyboard
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)  # Here we start our application
    GUI = MainWindow()  # At this moment mainWindow will be initialized
    sys.exit(app.exec_())  # We are passing app.exec because it will return our QApplication exit code to sys.exit call
