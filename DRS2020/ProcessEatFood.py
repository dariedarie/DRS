import math
import time
import multiprocessing as mp
from Models.Snake import Snake
from Models.Food import Food


class ProcessEatFood(mp.Process):

    def __init__(self, in_q: mp.Queue, out_q: mp.Queue, ):
        super().__init__(target=self.__checkFood__, args=[in_q, out_q])

    def __checkFood__(self, in_q: mp.Queue, out_q: mp.Queue):

        while True:
            temp = False
            tp = None
            while not in_q.empty():
                tp = in_q.get()
            if tp is not None:
                snakes = tp[0]
                food = tp[1]
                for f in range(len(food)):
                    for s in range(len(snakes)):
                        if food[f][0] == snakes[s][0] and food[f][1] == snakes[s][1]:
                            out_q.put([food[f][0], food[f][1], snakes[s][0], snakes[s][1]]) # food.x,food.y,snake.head.x,sneak.head.y
                            temp = True
                            time.sleep(0.1)
                            break
                    if temp:
                        time.sleep(0.1)
                        break;
                time.sleep(0.01)
                out_q.put([-1, -1])
