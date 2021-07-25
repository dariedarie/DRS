from Worker import Worker
import multiprocessing as mp
import time
from Models.Snake import Snake
from Models.Food import Food
import socket, select, selectors, types


class ServerCommsWorker(Worker):
    def __init__(self, s, to_send_messages_queue: mp.Queue, to_receive_messages_queue: mp.Queue):
        super().__init__()
        self.ssocket = s
        self.to_send = to_send_messages_queue
        self.to_receive = to_receive_messages_queue
        self.sel = selectors.DefaultSelector()

    def work(self):
        self.ssocket.setblocking(False)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(inb=b'',
                                     recv_total=0,
                                     outb=b'')
        self.sel.register(self.ssocket, events, data=data)
        while True:
            try:
                events = self.sel.select(timeout=0)
                for key, mask in events:
                   self.service_connection(key, mask)
                time.sleep(0.0001)
            except Exception:
                pass

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                self.to_receive.put(recv_data.decode())
                self.update.emit()
            """if not recv_data:
                print('closing connection')
                self.sel.unregister(sock)
                sock.close()"""
        if mask & selectors.EVENT_WRITE:
            if not self.to_send.empty():
                sendstring = self.to_send.get()
                sock.send(sendstring.encode())
            else:
                pass
