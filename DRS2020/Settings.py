import os
import subprocess
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QDesktopWidget, QComboBox, QMessageBox, QLabel, \
    QVBoxLayout, QInputDialog, QSpinBox, QGraphicsItem
from PyQt5.QtGui import QPixmap, QCursor, QKeyEvent, QFont, QImage, QBrush, QColor, QIcon
from PyQt5.QtCore import Qt, QRectF
import sys
import time
from GameWindow import GameWindow
from LoadingScreen import LoadingScreen

class SettingsWindow(QMainWindow):
    SettingsWindowH = 600
    SettingsWindowW = 800

    def __init__(self, mainwind):  # Here we initialize MainWindow class
        super(SettingsWindow, self).__init__()  # Here we initialize base class (Super class)  i.e QWidget
        self.resize(self.SettingsWindowH, self.SettingsWindowW)
        self.setMinimumHeight(self.SettingsWindowH)
        self.setMinimumWidth(self.SettingsWindowW)
        self.setMaximumHeight(self.SettingsWindowH)
        self.setMaximumWidth(self.SettingsWindowW)
        self.setWindowTitle("Choose number of players and snakes")
        self.setStyleSheet("background-color: black;")
        self.setWindowIcon(QIcon('resources/icon.png'))
        self.spin = QSpinBox(self)
        self.spin.setGeometry(350, 100, 100, 40)
        self.spin.setMinimum(2)
        self.spin.setMaximum(4)
        self.spin.valueChanged.connect(self.show_result)
        self.spin.setStyleSheet("background-color: lightgreen; border:2px solid blue;")

        self.label_1 = QLabel('Number of players', self)
        self.label_1.setFont(QFont('Calibri', 10))
        self.label_1.move(320, 80)
        self.label_1.resize(165, 20)
        self.label_1.setStyleSheet("background-color: lightgreen; ")

        self.numberOfSnakes = 1
        self.numberOfPlayers = 2

        self.spin_2 = QSpinBox(self)
        self.spin_2.setGeometry(350, 200, 100, 40)
        self.spin_2.setMinimum(1)
        self.spin_2.setMaximum(3)
        self.spin_2.valueChanged.connect(self.show_result_2)
        self.spin_2.setStyleSheet("background-color: lightgreen; border:2px solid blue;")

        self.label_2 = QLabel('Number of snakes', self)
        self.label_2.setFont(QFont('Calibri', 10))
        self.label_2.move(320, 180)
        self.label_2.resize(165, 20)
        self.label_2.setStyleSheet("background-color: lightgreen")

        self.continueButton = QtWidgets.QPushButton("", self)
        self.continueButton.setStyleSheet(
            "border:2px solid blue; color: " "blue;font-size: 27px; font-family: Calibri; "
            "background-image: url(resources/ContinueButton.jpg);")
        self.continueButton.setGeometry(275, 340, 250, 50)
        self.continueButton.setCursor(Qt.PointingHandCursor)
        self.continueButton.released.connect(self.run)
        # self.center()
        self.setGeometry(mainwind.geometry())
        # show all the widgets
        self.show()

    def show_result(self):
        # getting current value
        self.numberOfPlayers = self.spin.value()
        # setting value of spin box to the label

    def center(self):
        screen = QDesktopWidget().screenGeometry()  # Here we take our full screen geometry
        size = self.geometry()  # Here we take our app geometry
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    def show_result_2(self):
        # getting current value
        self.numberOfSnakes = self.spin_2.value()

    def run(self):
        subprocess.Popen("python GameServer.py numberOfPlayers={0} numberOfSnakes={1}".format(self.numberOfPlayers,
                                                                                              self.numberOfSnakes))
        time.sleep(1)
        self.loadWindow = LoadingScreen(self.geometry(),self.numberOfPlayers, self.numberOfSnakes, '-1')

        self.hide()
