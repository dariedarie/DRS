import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import socket

from Models.Food import Food
from Models.ForcePointer import ForcePointer
from Models.Snake import *
from Models.Block import Block, BlockType
import random
import sys

# creating game window
from Models.Snake import Snake
from Models.UnexpectedForce import Force
from ProcessForce import ProcessForce
from Worker import Worker
from WorkerEatFood import WorkerEatFood
from multiprocessing import Queue
from ProcessEatFood import ProcessEatFood
from CollisionWorker import CollisionWorker
from CollisionProcess import CollisionProcess
from ServerCommsWorker import ServerCommsWorker
from WorkerForce import WorkerForce

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432  # The port used by the server


class GameWindow(QMainWindow):
    GameWindowH = 600
    GameWindowW = 800

    def __init__(self, numberOfPlayers, numberOfSnakes, lastwind):
        super(GameWindow, self).__init__()
        self.setGeometry(lastwind.geometry())
        self.myUniqueID = lastwind.myUniqueID
        self.currentIDPlaying = -1  # to block and unblock gameplay
        self.timeCounter = -1

        self.timerForMove = QBasicTimer()
        self.firstTimeGotID = True
        self.numOfPlayers = numberOfPlayers
        self.numOfSnakes = numberOfSnakes
        self.afkDeadCounter = 0

        # added more variables to track current and max moves of player
        # at start all snakes have max 2 moves [ [p1s1,p1s2,p1s3], [p2s1,p2s2,p2s3] ]
        # self.maxMovesPerSnake = [[0] * numberOfSnakes for i in range(numberOfPlayers)]
        # self.movesMadePerSnake = [[0] * numberOfSnakes for i in range(numberOfPlayers)]
        self.maxMovesPerSnake = []
        self.movesMadePerSnake = []
        self.amIDead = False
        self.DidIMadeMOve = False
        for i in range(self.numOfSnakes):
            self.maxMovesPerSnake.append(3)
            self.movesMadePerSnake.append(0)

        # setting geometry to the window
        # screen = QDesktopWidget().screenGeometry()
        # self.setGeometry(100, 100, screen.width(), screen.height())
        # self.setStyleSheet("background-image: url(resources/mapa.jpg);")
        self.setWindowIcon(QIcon('resources/icon.png'))
        oImage = QImage("resources/mapa.jpg")
        sImage = oImage.scaled(QSize(800, 600))  # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(10, QBrush(sImage))  # 10 = WindowRole
        self.setPalette(palette)
        self.resize(self.GameWindowH, self.GameWindowW)
        self.setMinimumHeight(self.GameWindowH)
        self.setMinimumWidth(self.GameWindowW)
        self.setMaximumHeight(self.GameWindowH)
        self.setMaximumWidth(self.GameWindowW)
        self.setWindowTitle('Game window')
        self.s = lastwind.s
        vb = QVBoxLayout()
        w = QWidget()
        hb = QHBoxLayout()

        self.iAmLabel = QLabel()
        self.iAmLabel.setFont(QFont('Times', 14))
        self.iAmLabel.setText("I am Player {0}".format(self.myUniqueID + 1))
        self.iAmLabel.setAlignment(Qt.AlignHCenter)
        vb.addWidget(self.iAmLabel)
        self.whoIsPlayingLabel = QLabel()
        self.whoIsPlayingLabel.setWordWrap(True)
        self.whoIsPlayingLabel.setFont(QFont('Times', 14))
        self.whoIsPlayingLabel.setText("Playing: Game is starting...")
        self.whoIsPlayingLabel.setAlignment(Qt.AlignHCenter)

        vb.addWidget(self.whoIsPlayingLabel)

        hb.addLayout(vb)
        self.grid = QGridLayout()

        hb.addLayout(self.grid)
        w.setLayout(hb)
        w.layout().setContentsMargins(0, 0, 0, 0)
        w.layout().setSpacing(0)
        self.setCentralWidget(w)
        self.iAmLabel.move(QPoint(0, 0))
        self.whoIsPlayingLabel.move(QPoint(0, 5))

        self.init_map()

        self.Players = {PlayerID: [] for PlayerID in range(0, numberOfPlayers)}
        self.init_snakes()

        self.Food = []
        self.Snakes = []
        self.Force = []
        self.ForcePointer = []

        self.PlayerSnakeId = [self.myUniqueID, 0]

        for i in range(numberOfPlayers):
            self.Snakes.extend(self.Players[i])

        self.in_queue_eatfood = Queue()
        self.out_queue_eatfood = Queue()

        self.EatFoodProcess = ProcessEatFood(self.in_queue_eatfood, self.out_queue_eatfood)
        self.EatFoodProcess.start()

        self.eatFoodWorker = WorkerEatFood(self.Food, self.Snakes, self.maxMovesPerSnake, self.PlayerSnakeId,
                                           self.myUniqueID, self.in_queue_eatfood, self.out_queue_eatfood, self.grid)
        self.eatFoodWorker.update.connect(self.receive_from_eatfood_worker)
        self.eatFoodWorker.start()
        self.signalCounter = 0

        self.in_queue_eatforce = Queue()
        self.out_queue_eatforce = Queue()

        self.ForceProcess = ProcessForce(self.in_queue_eatforce, self.out_queue_eatforce)
        self.ForceProcess.start()

        self.ForceWorker = WorkerForce(self.Force, self.Players, self.Snakes, self.maxMovesPerSnake, self.PlayerSnakeId,
                                       self.myUniqueID, self.in_queue_eatforce, self.out_queue_eatforce, self.grid)
        self.ForceWorker.update.connect(self.receive_from_eatforce_worker)
        self.ForceWorker.start()



        self.KeyStrokes = []
        # Setting up process and worker to check up on collisions
        self.in_queue_collision = Queue()
        self.out_queue_collision = Queue()

        self.CollisionProcess = CollisionProcess(self.in_queue_collision, self.out_queue_collision)
        self.CollisionProcess.start()

        # self.SnakeOnMove = self.Players[self.myUniqueID][0]

        self.Players[self.myUniqueID][self.PlayerSnakeId[1]].on_off_move(self.grid)
        self.CollisionWorker = CollisionWorker(self.myUniqueID, self.Players, self.PlayerSnakeId, self.grid,
                                               self.KeyStrokes, self.Snakes, self.maxMovesPerSnake,
                                               self.movesMadePerSnake, self.in_queue_collision,
                                               self.out_queue_collision)
        self.CollisionWorker.update.connect(self.receive_from_collision_worker)
        self.CollisionWorker.start()
        self.signalFromCollision = 0

        self.comms_to_send_queue = Queue()
        self.comms_to_receive_queue = Queue()
        self.CommsWorker = ServerCommsWorker(self.s, self.comms_to_send_queue, self.comms_to_receive_queue)
        self.CommsWorker.update.connect(self.receive_from_communication_worker)
        self.CommsWorker.start()

        self.show()

    def init_map(self):
        # Add positions to the map
        for x in range(0, 15):
            for y in range(0, 15):
                w = Block(x, y)
                self.grid.addWidget(w, x, y)

    def init_players(self):
        for i in range(0, self.numOfPlayers):
            self.ListOfPlayers.append(i)

    def init_snakes(self):
        for player_id, snakes in self.Players.items():
            for snake_id in range(0, self.numOfSnakes):
                s = Snake()
                s.init_snake(self.grid, player_id, snake_id)
                snakes.append(s)
        self.update()

    def closeEvent(self, event):
        close = QMessageBox.question(self,
                                     "QUIT",
                                     "Sure?",
                                     QMessageBox.Yes | QMessageBox.No)
        if close == QMessageBox.Yes:
            self.eatFoodWorker.thread.terminate()
            self.EatFoodProcess.terminate()
            self.ForceWorker.thread.terminate()
            self.ForceProcess.terminate()
            self.CollisionWorker.thread.terminate()
            self.CollisionProcess.terminate()
            self.CommsWorker.thread.terminate()
            self.s.close()
            event.accept()
        else:
            event.ignore()

    def timerEvent(self, event):
        if self.timerForMove.timerId() == event.timerId():  # One second passed
            self.timeCounter = self.timeCounter - 1
            playerNumber = self.currentIDPlaying + 1
            if not self.amIDead:
                self.whoIsPlayingLabel.setText("Playing: Player {0}\nTime left:{1}".format(playerNumber,
                                                                                           self.timeCounter))
            else:
                self.whoIsPlayingLabel.setStyleSheet("QLabel { color : red; }")
                self.whoIsPlayingLabel.setText(
                    "You are dead.Waiting for others to finish.\nPlaying: Player {0}\nTime left:{1}".format(
                        playerNumber,
                        self.timeCounter))
            if self.timeCounter <= 0:
                if self.myUniqueID == self.currentIDPlaying:
                    if not self.DidIMadeMOve:
                        print("I haven't made move.")
                        try:
                            self.afkDeadCounter = self.afkDeadCounter + 1
                            if self.afkDeadCounter == 3:
                                time.sleep(0.05)
                                playerNumber = self.currentIDPlaying + 1
                                self.amIDead = True
                                self.whoIsPlayingLabel.setStyleSheet("QLabel { color : red; }")
                                self.whoIsPlayingLabel.setText(
                                    "You are dead.Waiting for others to finish.\nPlaying: Player {0}\nTime left:{1}".format(
                                        playerNumber,
                                        self.timeCounter))
                                sendAfkSignal = "AfkDisc/{0};".format(self.myUniqueID)
                                self.comms_to_send_queue.put(sendAfkSignal)
                        except Exception as e:
                            pass
                self.whoIsPlayingLabel.setText("Playing: Changing Player")
                self.currentIDPlaying = -1  # blocking players till turn change
                self.DidIMadeMOve = False
                for i in range(len(self.Food)):
                    currX = self.Food[i].x
                    currY = self.Food[i].y
                    found = False
                    securityCounter = 0
                    b = self.grid.itemAtPosition(currX, currY).widget()
                    while True:
                        delta = random.randint(-3, 3)
                        xyChoose = random.randint(0, 1)
                        if xyChoose == 0:
                            newX = currX + delta
                            newY = currY
                            if newX <= 14 and newY <= 14 and newY >= 0 and newX >= 0:
                                b = self.grid.itemAtPosition(newX, newY).widget()
                                if b.BType == BlockType.EmptyBlock:
                                    found = True
                                    break
                                if securityCounter == 20:
                                    break
                                else:
                                    securityCounter = securityCounter + 1
                        else:
                            newX = currX
                            newY = currY + delta
                            if newX <= 14 and newY <= 14 and newY >= 0 and newX >= 0:
                                b = self.grid.itemAtPosition(newX, newY).widget()
                                if b.BType == BlockType.EmptyBlock:
                                    found = True
                                    break
                                if securityCounter == 20:
                                    break
                                else:
                                    securityCounter = securityCounter + 1

                    if found:
                        sendMoveFoodReq = "MoveFood/{0}/{1}/{2}/{3}/{4};".format(self.myUniqueID, currX,
                                                                                 currY, newX, newY)

                        self.comms_to_send_queue.put(sendMoveFoodReq)
                        time.sleep(0.05)

    def drop_food(self, x, y):
        b = self.grid.itemAtPosition(x, y).widget()

        if b.BType == BlockType.EmptyBlock:
            self.Food.append(Food(b))
            self.update()
        else:
            sendFoodReq = "FoodRequest/{0};".format(self.myUniqueID)  # request and id to see is player coord
            self.comms_to_send_queue.put(sendFoodReq)
            time.sleep(0.05)

    def drop_force(self, x, y, effect):
        b = self.grid.itemAtPosition(x, y).widget()

        if b.BType == BlockType.ForcePointer:
            f = Force(b)
            f.effect = effect
            self.Force.append(f)
            self.update()
        else:
            temp = self.ForcePointer[-1]
            sendForceReq = "ForceRequest/{0}/{1}/{2};".format(self.myUniqueID, temp.x, temp.y)
            self.comms_to_send_queue.put(sendForceReq)
            time.sleep(0.05)

    def drop_forcePointer(self, x, y):
        b = self.grid.itemAtPosition(x, y).widget()

        if b.BType == BlockType.EmptyBlock:
            self.ForcePointer.append(ForcePointer(b))
            self.update()
        else:
            sendForcePointerReq = "PointerRequest/{0};".format(self.myUniqueID)
            self.comms_to_send_queue.put(sendForcePointerReq)
            time.sleep(0.05)

    def keyPressEvent(self, e: QKeyEvent):
        if self.myUniqueID == self.currentIDPlaying:
            if len(self.Players[self.myUniqueID]) != 0:
                cought_key = e.key()
                if cought_key == Qt.Key_Space:
                    self.Players[self.myUniqueID][self.PlayerSnakeId[1]].on_off_move(self.grid)
                    self.PlayerSnakeId[1] += 1
                    if self.PlayerSnakeId[1] == len(self.Players[self.myUniqueID]):
                        self.PlayerSnakeId[1] = 0
                    self.Players[self.myUniqueID][self.PlayerSnakeId[1]].on_off_move(self.grid)
                    self.update()
                elif cought_key == Qt.Key_Up or cought_key == Qt.Key_Down or cought_key == Qt.Key_Left or cought_key == Qt.Key_Right:
                    if self.movesMadePerSnake[self.PlayerSnakeId[1]] \
                            < self.maxMovesPerSnake[self.PlayerSnakeId[1]] and\
                            self.possible_move(self.Players[self.myUniqueID][self.PlayerSnakeId[1]].last_move, cought_key):
                        self.DidIMadeMOve = True
                        self.afkDeadCounter = 0
                        self.KeyStrokes.append(cought_key)
                        sendString = "Command/{0}/{1}/{2};".format(QKeySequence(e.key()).toString(), self.myUniqueID,
                                                                   self.PlayerSnakeId[1])  # kasnije resiti id zmije
                        self.movesMadePerSnake[self.PlayerSnakeId[1]] = \
                            self.movesMadePerSnake[self.PlayerSnakeId[1]] + 1
                        #  print("Move made.")
                        #  print(self.movesMadePerSnake)
                        self.comms_to_send_queue.put(sendString)
                time.sleep(0.05)

    @pyqtSlot()
    def receive_from_eatfood_worker(self):
        print("Signal received ")
        print(self.signalCounter)

        # self.Snakes[0].body_increase(self.grid)
        print("\n Food count ")
        print(len(self.Food))
        self.signalCounter = self.signalCounter + 1

    @pyqtSlot()
    def receive_from_eatforce_worker(self):
        print("Signal received ")
        print(self.signalCounter)

        # self.Snakes[0].body_increase(self.grid)
        print("\n Force count ")
        print(len(self.Force))
        self.signalCounter = self.signalCounter + 1

    @pyqtSlot()
    def receive_from_collision_worker(self):
        print("Signal from collision worker recieved")
        self.update()
        if len(self.Players[self.myUniqueID]) == 0:  # player died
            iAmDead = "Died/{0};".format(self.myUniqueID)
            self.comms_to_send_queue.put(iAmDead)
            time.sleep(0.05)
            playerNumber = self.currentIDPlaying + 1
            self.amIDead = True
            self.whoIsPlayingLabel.setStyleSheet("QLabel { color : red; }")
            self.whoIsPlayingLabel.setText(
                "You are dead.Waiting for others to finish.\nPlaying: Player {0}\nTime left:{1}".format(playerNumber,
                                                                                                        self.timeCounter))
        # print(self.signalFromCollision)
        self.signalFromCollision = self.signalFromCollision + 1

    @pyqtSlot()
    def receive_from_communication_worker(self):
        # print("Signal from comm worker received")
        raw_data = self.comms_to_receive_queue.get()
        messages = raw_data.split(";")

        for message in messages[:-1]:
            print("Received: ", message)
            if "Playing" in message:
                # da obavi i poslednji korak prethodnog igraca pre nego se igra nastavi i promene bitni parametri
                time.sleep(0.5)
                self.KeyStrokes.clear()  # moze se desiti da zaostanu neki key-evi u listi i dodje do desinhronizacije
                splitlist = message.split("/")
                playerNumber = int(splitlist[1])
                self.currentIDPlaying = playerNumber
                playerNumber = playerNumber + 1  # for nice print
                self.timeCounter = 11
                self.whoIsPlayingLabel.setText(
                    "Playing: Player {0}\nTime left:{1}".format(playerNumber, self.timeCounter))
                for i in range(len(self.Players[self.myUniqueID])):
                    self.movesMadePerSnake[i] = 0
                if self.firstTimeGotID:
                    self.timerForMove.start(1000, self)
                    self.firstTimeGotID = False

                if self.currentIDPlaying == self.myUniqueID:
                    for s in range(0, len(self.Players[self.myUniqueID])):
                        if self.Players[self.myUniqueID][s].OnMove:
                            self.Players[self.myUniqueID][s].on_off_move(self.grid)
                    self.Players[self.myUniqueID][0].on_off_move(self.grid)
                    self.update()

                self.PlayerSnakeId[0] = self.currentIDPlaying
                self.PlayerSnakeId[1] = 0
            elif "DropFood" in message:
                splitlist = message.split("/")
                xf = int(splitlist[1])
                yf = int(splitlist[2])
                self.drop_food(xf, yf)
            elif "Force" in message:
                splitlist = message.split("/")
                xf = int(splitlist[1])
                yf = int(splitlist[2])
                eff = int(splitlist[3])
                self.drop_force(xf, yf, eff)
            elif "Pointer" in message:
                splitlist = message.split("/")
                xf = int(splitlist[1])
                yf = int(splitlist[2])
                self.drop_forcePointer(xf, yf)
            elif "Command" in message:
                splitlist = message.split("/")
                key = splitlist[1]
                commandPlayerID = int(splitlist[2])
                commandSnakeID = int(splitlist[3])
                #  print("Command received: {0}, Player ID: {1}, Snake ID:{2}".format(key, commandPlayerID,commandSnakeID))
                self.PlayerSnakeId[0] = commandPlayerID
                self.PlayerSnakeId[1] = commandSnakeID

                if key == 'Left':
                    self.KeyStrokes.append(Qt.Key_Left)
                elif key == 'Right':
                    self.KeyStrokes.append(Qt.Key_Right)
                elif key == 'Up':
                    self.KeyStrokes.append(Qt.Key_Up)
                elif key == 'Down':
                    self.KeyStrokes.append(Qt.Key_Down)
            elif "MoveFood" in message:
                splitlist = message.split("/")
                oldX = int(splitlist[1])
                oldY = int(splitlist[2])
                newX = int(splitlist[3])
                newY = int(splitlist[4])
                for f in self.Food:
                    if f.x == oldX and f.y == oldY:
                        self.Food.remove(f)
                b = self.grid.itemAtPosition(oldX, oldY).widget()
                b.BType = BlockType.EmptyBlock
                b = self.grid.itemAtPosition(newX, newY).widget()
                self.Food.append(Food(b))
                self.update()
            elif "GameOver" in message:
                self.timerForMove.stop()

                splitlist = message.split("/")
                winnerid = int(splitlist[1])
                if self.myUniqueID == winnerid:
                    self.whoIsPlayingLabel.setStyleSheet("QLabel { color : blue; }")
                    self.whoIsPlayingLabel.setText("Congratulations! You won the game!")
                else:
                    self.whoIsPlayingLabel.setStyleSheet("QLabel { color : red; }")
                    self.whoIsPlayingLabel.setText("Game over. Player {0} won the game.".format(winnerid+1))
            elif "KillSnakes" in message:
                splitlist = message.split("/")
                deathid = int(splitlist[1])
                for i in range(len(self.Players[deathid])):
                    self.Players[deathid][i].kill_snake(self.grid)
                self.Players[deathid].clear()
                self.update()
            elif message == "":
                pass
            else:
                print("Message not recognized")

    @staticmethod
    def possible_move(old_dir, new_dir):
        if new_dir == Qt.Key_Up:
            if old_dir == 'd':
                return False
            return True
        elif new_dir == Qt.Key_Down:
            if old_dir == 'u':
                return False
            return True
        elif new_dir == Qt.Key_Left:
            if old_dir == 'r':
                return False
            return True
        elif new_dir == Qt.Key_Right:
            if old_dir == 'l':
                return False
            return True
