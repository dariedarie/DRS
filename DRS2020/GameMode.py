from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QDesktopWidget, QComboBox, QMessageBox, QLabel, \
    QVBoxLayout, QInputDialog, QSpinBox, QGraphicsItem
from PyQt5.QtGui import QPixmap, QCursor, QKeyEvent, QFont, QImage, QBrush, QColor, QIcon
from PyQt5.QtCore import Qt, QRectF
import sys
from Settings import SettingsWindow
from GameWindow import GameWindow
from LoadingScreen import LoadingScreen
import socket

class GameModeWindow(QMainWindow):
    WindowH = 600
    WindowW = 800

    def __init__(self, mainwind):  # Here we initialize MainWindow class
        super(GameModeWindow, self).__init__()  # Here we initialize base class (Super class)  i.e QWidget
        self.setMinimumHeight(self.WindowH)
        self.setMinimumWidth(self.WindowW)
        self.setMaximumHeight(self.WindowH)
        self.setMaximumWidth(self.WindowW)
        self.setWindowTitle("Create game or join one")
        self.setStyleSheet("background-color: black;")
        self.setWindowIcon(QIcon('resources/icon.png'))

        self.singlePlayerButton = QtWidgets.QPushButton("", self)
        self.singlePlayerButton.setStyleSheet(
            "border:2px solid blue; color: " "blue;font-size: 27px; font-family: Calibri; "
            "background-image: url(resources/createGame.jpg);")
        self.singlePlayerButton.setGeometry(275, 200, 250, 50)
        self.singlePlayerButton.setCursor(Qt.PointingHandCursor)
        self.singlePlayerButton.released.connect(self.run)

        self.multiPlayerButton = QtWidgets.QPushButton("", self)
        self.multiPlayerButton.setStyleSheet(
            "border:2px solid blue; color: " "blue;font-size: 27px; font-family: Calibri; "
            "background-image: url(resources/joinGame.jpg);")
        self.multiPlayerButton.setGeometry(275, 300, 250, 50)
        self.multiPlayerButton.setCursor(Qt.PointingHandCursor)
        self.multiPlayerButton.released.connect(self.joinGame)
        # self.center()
        self.setGeometry(mainwind.geometry())

        self.show()

    def center(self):
        screen = QDesktopWidget().screenGeometry()  # Here we take our full screen geometry
        size = self.geometry()  # Here we take our app geometry
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    # noinspection PyMethodMayBeStatic
    def run(self):
        # print("Run Run")
        self.Settings = SettingsWindow(self)
        self.hide()

    def joinGame(self):
        ip = '-1'
        self.setStyleSheet("QInputDialog {background-color: green;};")
        address, ok = QInputDialog.getText(self,'Server IP address: ',
                                           'Enter server IP address (For local server leave empty): ')
        if ok:
            try:
                socket.inet_aton(address)
                print("Manually entered ip address: ", address)
                ip = address
            except socket.error:
                ip = '-1'
        else:
            ip = '-1'
        self.gameWindow = LoadingScreen(self.geometry(), -1, -1, ip)

        self.hide()
