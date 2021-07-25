import math
import time
import multiprocessing as mp
from Models.Snake import Snake
from Models.Food import Food


class ProcessForce(mp.Process):

    def __init__(self, in_q: mp.Queue, out_q: mp.Queue, ):
        super().__init__(target=self.__checkForce__, args=[in_q, out_q])

    def __checkForce__(self, in_q: mp.Queue, out_q: mp.Queue):

        while True:
            temp = False
            tp = None
            while not in_q.empty():
                tp = in_q.get()
            if tp is not None:
                snakes = tp[0]
                force = tp[1]
                for f in range(len(force)):
                    for s in range(len(snakes)):
                        if force[f][0] == snakes[s][0] and force[f][1] == snakes[s][1]:
                            out_q.put([force[f][0], force[f][1], snakes[s][0], snakes[s][1]], force[f][2])
                            temp = True
                            time.sleep(0.1)
                            break
                    if temp:
                        time.sleep(0.1)
                        break;
                time.sleep(0.01)
                out_q.put([-1, -1])