import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import socket
from GameWindow import GameWindow
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432  # The port used by the server


class LoadingScreen(QMainWindow):

    def __init__(self, geom, numberOfPlayers, numberOfSnakes, selectedIP):
        super().__init__()
        global HOST
        self.setFixedSize(800, 600)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        if selectedIP == '-1':
            HOST = '127.0.0.1'
        else:
            HOST = selectedIP
        self.myUniqueID = -1
        self.numOfPlayers = numberOfPlayers
        self.numOfSnakes = numberOfSnakes

        # Primamo od servera info o broju zmija,igraca i nas id
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        data = self.s.recv(1024)
        dataString = data.decode()
        nPnS = dataString.split(";")
        self.numOfPlayers = int(nPnS[0])
        self.numOfSnakes = int(nPnS[1])
        self.myUniqueID = int(nPnS[2])
        print("Server sent information. Number of players: ", self.numOfPlayers)
        print("Server sent information. Number of snakes: ", self.numOfSnakes)
        print("Server sent information. Player unique ID: ", self.myUniqueID)

        self.conntimer = QBasicTimer()
        self.conntimer.start(1000, self)
        self.label_animation = QLabel(self)
        self.wfpgif = QMovie('resources/waitingforplayers.gif')
        self.label_animation.setMovie(self.wfpgif)
        self.setCentralWidget(self.label_animation)
        self.setGeometry(geom)
        self.startAnimation()
        self.show()

    def startAnimation(self):
        self.wfpgif.start()

    def stopAnimation(self):
        self.wfpgif.stop()

    def timerEvent(self, event):
        if event.timerId() == self.conntimer.timerId():
            try:
                self.s.settimeout(0.1)
                data = self.s.recv(1024)
                dataString = data.decode()
                if dataString == "GO":
                    self.stopAnimation()
                    self.s.settimeout(socket.getdefaulttimeout())
                    self.gameWindow = GameWindow(self.numOfPlayers,self.numOfSnakes,self)
                    self.conntimer.stop()  # Ovde treba da se doda i da se promeni neka
                    # promenjiva koja oznacava pocetak i onda moze da
                    # se spawnuje hrana i zmije krecu
                    self.hide()
                else:
                    pass
            except socket.timeout:
                pass
