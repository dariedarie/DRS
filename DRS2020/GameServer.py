import socket
import selectors
import sys
import types
import time
import threading
import random

from PyQt5.QtCore import *

# HOST = '127.0.0.1'
HOST = '0.0.0.0'
PORT = 65432
sel = selectors.DefaultSelector()

lock = threading.Lock()
GameOverSignal = False
numberOfPlayersString = sys.argv[1]
numberOfPlayers = int(numberOfPlayersString[16:])
numberOfSnakesString = sys.argv[2]
numberOfSnakes = int(numberOfSnakesString[15:])
PlayerSockets = []

PlayersAliveStatus = []
PlayersAliveCounter = numberOfPlayers

PlayerCoordinator = 0  # when first player dies, second became coord
for i in range(numberOfPlayers):
    PlayersAliveStatus.append(True)

timerMove = QTimer()

print("Server starting. Number of players: {0}. Number of snakes per each player: {1}".format(int(numberOfPlayers),
                                                                                              int(numberOfSnakes)))
# Server logic


def accept_wrapper(sock):  # Accepting clients and making sockets non-blocking
    conn, addr = sock.accept()
    print("Player connected from address: ", addr)
    print("Player got ID: ", len(PlayerSockets))

    sts = "{0};{1};{2}".format(numberOfPlayers, numberOfSnakes, len(PlayerSockets))
    conn.sendall(sts.encode())
    conn.setblocking(False)  # We dont wanna players to block our server
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    # We will only check in main server thread are there messages to read bcs send is time controlled
    events = selectors.EVENT_READ
    sel.register(conn, events, data=data)
    PlayerSockets.append(conn)


def receive_message(key, mask):  # Handling incoming msgs from clients
    sock = key.fileobj
    data = key.data
    global GameOverSignal
    global PlayerCoordinator
    global PlayersAliveCounter
    if mask & selectors.EVENT_READ:  # If we have something to receive from clients
        with lock:
            recv_data = sock.recv(1024)  # Receive
            if recv_data:
                recvString = recv_data.decode()
                messages = recvString.split(";")
                for message in messages[:-1]:
                    print("Server received: ", message)
                    if "Command" in message:
                        splitStrings = message.split("/")
                        command = splitStrings[1]
                        playerID = splitStrings[2]
                        snakeId = splitStrings[3]
                        stsc = "Command/{0}/{1}/{2};".format(command, int(playerID), int(snakeId))
                        for sck in PlayerSockets:
                            if sck != PlayerSockets[int(playerID)]:
                                sck.send(stsc.encode())
                    elif "FoodRequest" in message:
                        splitStrings = message.split("/")
                        command = splitStrings[0]
                        reqID = int(splitStrings[1])
                        if reqID == PlayerCoordinator:
                            xf, yf = random.randint(0, 14), random.randint(0, 14)
                            counterFood = 0
                            fsts = "DropFood/{0}/{1};".format(xf, yf)
                            for sck in PlayerSockets:
                                sck.send(fsts.encode())
                    elif "ForceRequest" in message:
                        effect = random.randint(0, 1)
                        splitStrings = message.split("/")
                        command = splitStrings[0]
                        reqID = int(splitStrings[1])
                        xf = int(splitStrings[2])
                        yf = int(splitStrings[3])
                        if reqID == PlayerCoordinator:
                            #xf, yf = random.randint(0, 14), random.randint(0, 14)
                            fsts = "Force/{0}/{1}/{2};".format(xf, yf, effect)
                            for sck in PlayerSockets:
                                sck.send(fsts.encode())
                    elif "PointerRequest" in message:
                        splitStrings = message.split("/")
                        command = splitStrings[0]
                        reqID = int(splitStrings[1])
                        if reqID == PlayerCoordinator:
                            xf, yf = random.randint(0, 14), random.randint(0, 14)
                            counterForcePointer = 0
                            fsts = "Pointer/{0}/{1};".format(xf, yf)
                            for sck in PlayerSockets:
                                sck.send(fsts.encode())
                    elif "MoveFood" in message:
                        splitStrings = message.split("/")
                        command = splitStrings[0]
                        reqID = int(splitStrings[1])
                        if reqID == PlayerCoordinator:
                            oldX = int(splitStrings[2])
                            oldY = int(splitStrings[3])
                            newX = int(splitStrings[4])
                            newY = int(splitStrings[5])
                            fsts = "MoveFood/{0}/{1}/{2}/{3};".format(oldX, oldY, newX, newY)
                            for sck in PlayerSockets:
                                sck.send(fsts.encode())
                    elif "Died" in message:
                        splitStrings = message.split("/")
                        command = splitStrings[0]
                        deathId = int(splitStrings[1])
                        if PlayersAliveStatus[deathId]:
                            PlayersAliveCounter = PlayersAliveCounter - 1
                            PlayersAliveStatus[deathId] = False
                            if PlayersAliveCounter == 1:
                                for k in range(len(PlayersAliveStatus)):
                                    if PlayersAliveStatus[k]:
                                        gameovermsg = "GameOver/{0};".format(k)
                                        for sck in PlayerSockets:
                                            sck.send(gameovermsg.encode())
                                        GameOverSignal = True
                                        break
                            else:
                                for k in range(len(PlayersAliveStatus)):
                                    if PlayersAliveStatus[k]:
                                        PlayerCoordinator = k
                                        print("Changed coordinator to: ", PlayerCoordinator)
                                        break
                    elif "AfkDisc" in message:
                        splitStrings = message.split("/")
                        command = splitStrings[0]
                        deathId = int(splitStrings[1])
                        splitStrings = message.split("/")
                        command = splitStrings[0]
                        deathId = int(splitStrings[1])
                        if PlayersAliveStatus[deathId]:
                            PlayersAliveCounter = PlayersAliveCounter - 1
                            PlayersAliveStatus[deathId] = False
                            if PlayersAliveCounter == 1:
                                for k in range(len(PlayersAliveStatus)):
                                    if PlayersAliveStatus[k]:
                                        gameovermsg = "GameOver/{0};".format(k)
                                        for sck in PlayerSockets:
                                            sck.send(gameovermsg.encode())
                                        GameOverSignal = True
                                        break
                            else:
                                killsnakesmsg = "KillSnakes/{0};".format(deathId)
                                for sck in PlayerSockets:
                                    sck.send(killsnakesmsg.encode())
                        else:
                            for k in range(len(PlayersAliveStatus)):
                                if PlayersAliveStatus[k]:
                                    PlayerCoordinator = k
                                    print("Changed coordinator to: ", PlayerCoordinator)
                                    break
                    else:
                        print("Message not recognized.")
            else:
                print('closing connection to', data.addr)
                PlayerSockets.remove(sock)
                sel.unregister(sock)
                sock.close()


def changePlayerAndSpawnFood(start_id, numberofplayers):
    time.sleep(1)
    counterFood = 2  # Every time when its 2, its passed 22 second so spawn food
   # counterForce = 3
    firstTime = True
    print("Thread started")
    while True:
        if firstTime:
            firstTime = False
            time.sleep(3)
        else:
            sts = "Playing/{0};".format(start_id)
            with lock:
                for sck in PlayerSockets:
                    sck.send(sts.encode())
            if counterFood == 2:
                xf, yf = random.randint(0, 14), random.randint(0, 14)
                counterFood = 0
                fsts = "DropFood/{0}/{1};".format(xf, yf)
                with lock:
                    for sck in PlayerSockets:
                        sck.send(fsts.encode())
            else:
                counterFood = counterFood + 1

          #  if counterForce == 3:
           #     xf, yf = random.randint(0, 14), random.randint(0, 14)
            #    counterForce = 0
             #   fsts = "Force/{0}/{1};".format(xf, yf)
              #  with lock:
               #     for sck in PlayerSockets:
                #        sck.send(fsts.encode())
            #else:
             #   counterForce = counterForce + 1
            start_id = (start_id+1) % numberofplayers
            while not PlayersAliveStatus[start_id]:
                start_id = (start_id + 1) % numberofplayers


            print(len(PlayerSockets))
            time.sleep(11)


def SpawnForce():
    time.sleep(1)
    counterForcePointer = 20
    should_drop = 0
    firstTime = True
    print("Thread started")
    while True:
        if firstTime:
            firstTime = False
            time.sleep(3)
        else:
            if should_drop == 1:
                effect = random.randint(0,1)
                fsts = "Force/{0}/{1}/{2};".format(xf, yf, effect)
                with lock:
                    for sck in PlayerSockets:
                        sck.send(fsts.encode())
                should_drop = 0

            if counterForcePointer == 20:
                xf, yf = random.randint(0, 14), random.randint(0, 14)
                counterForcePointer = 0
                should_drop = 1
                fsts = "Pointer/{0}/{1};".format(xf, yf)
                with lock:
                    for sck in PlayerSockets:
                        sck.send(fsts.encode())
            else:
                counterForcePointer = counterForcePointer + 1
            
            time.sleep(2)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while len(PlayerSockets) < numberOfPlayers:  # waiting for all players to connect
        accept_wrapper(s)

    for sck in PlayerSockets:
        sts = "GO"

        sck.sendall(sts.encode())
    time.sleep(3)
    x = threading.Thread(target=changePlayerAndSpawnFood, args=(0, numberOfPlayers))
    x.daemon = True
    x.start()

    y = threading.Thread(target=SpawnForce, args=())
    y.daemon = True
    y.start()

    while not GameOverSignal:
        # print("Msg received")
        try:
            events = sel.select(timeout=None)  # sel.select(timeout=None) blocks until there are incoming messages.
            for key, mask in events:
                receive_message(key, mask)
        except Exception as e:
            print(e)
            print("Server shutting down.")
            break

    for sock in PlayerSockets:
        PlayerSockets.remove(sock)
        sel.unregister(sock)
        sock.close()

    exit(0)



