from Worker import Worker
import multiprocessing as mp
import time


class CollisionWorker(Worker):
    def __init__(self, uid, players, player_snake_id, grid, keys, all_snakes, maxStepsMatrix, stepsMadeMatrix, input_q: mp.Queue, output_q: mp.Queue):
        super().__init__()
        self.myUniqueId = uid
        self.ps_id = player_snake_id
        self.players = players
        self.grid = grid
        self.keys = keys
        self.all_snakes = all_snakes
        self.input_q = input_q
        self.output_q = output_q
        self.MaxSteps = maxStepsMatrix
        self.StepsMade = stepsMadeMatrix

    def work(self):
        while True:
            if len(self.ps_id) == 2 and self.players[self.ps_id[0]]:
                #p_id = self.ps_id[0]
                #s_id = self.ps_id[1]
                snake = self.players[self.ps_id[0]][self.ps_id[1]]
                temp_head = [snake.head.x, snake.head.y]
                temp_tails = list(map(lambda s: [s.tail.x, s.tail.y], self.all_snakes))
                temp_body_parts = []
                for s in self.all_snakes:
                    temp_body_parts.extend(list(map(lambda b: [b.x, b.y], s.body)))
                temp_heads = list(map(lambda s: [s.head.x, s.head.y], self.all_snakes))
                temp_last_direction = snake.last_move

                self.input_q.put([temp_head, self.keys, temp_body_parts, temp_tails, temp_heads, temp_last_direction])
                ret_val = self.output_q.get()
                if ret_val[0] != -1:
                    if not isinstance(ret_val[0], str):
                        if snake.head.x == ret_val[0] and snake.head.y == ret_val[1]:
                            self.all_snakes.remove(snake)
                            self.players[self.ps_id[0]].remove(snake)
                            snake.kill_snake(self.grid)

                            self.keys.remove(ret_val[2])

                            if self.ps_id[0] == self.myUniqueId:
                                self.MaxSteps.remove(self.MaxSteps[self.ps_id[1]])
                                self.StepsMade.remove(self.StepsMade[self.ps_id[1]])
                                # print(self.MaxSteps)
                                # print(self.StepsMade)
                            self.ps_id[1] = 0
                            if self.players[self.ps_id[0]] and self.myUniqueId == self.ps_id[0]:
                                self.players[self.ps_id[0]][0].on_off_move(self.grid)
                    else:
                        if not ret_val[0] == '':
                            snake.move(self.grid, ret_val[0])
                        try:
                            self.keys.remove(ret_val[1])
                        except Exception:
                            pass

                    self.update.emit()

                    while not self.output_q.empty():
                        self.output_q.get()

            time.sleep(0.001)
