from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Models.Block import Block, BlockType, RotateDegrees
from enum import IntEnum
import random
import sys


class Head(Block):
    def __init__(self, parent, moved=RotateDegrees.Right, picture="resources/head.png"):
        Block.__init__(self, parent.x, parent.y)
        parent.BType = BlockType.Head
        parent.RDegrees = moved
        parent.SnakePart = picture
        self.degree = parent.RDegrees


class Body(Block):
    def __init__(self, parent, moved=RotateDegrees.Right, blk=BlockType.Body, picture="resources/body.png"):
        Block.__init__(self, parent.x, parent.y)
        parent.BType = blk
        parent.RDegrees = moved
        parent.SnakePart = picture
        self.degree = parent.RDegrees
        self.BlkType = parent.BType


class Tail(Block):
    def __init__(self, parent, moved=RotateDegrees.Right, picture="resources/tail.png", pointer=False):
        Block.__init__(self, parent.x, parent.y)
        parent.BType = BlockType.Tail
        self.BType = BlockType.Tail
        parent.RDegrees = moved
        parent.SnakePart = picture
        parent.OnMove = pointer
        self.degree = parent.RDegrees


class Snake:
    def __init__(self):
        self.head = None
        self.body = []
        self.tail = None
        self.eat = 0
        self.last_move = 'r'
        self.killed = False
        self.headPicture = ""
        self.bodyPicture = ""
        self.curvedBodyPicture = ""
        self.tailPicture = ""
        self.OnMove = False

    def move(self, grid, direction):           
        # Smestamo postojece delove tela u lokalne promenljive
        saved_head = self.head
        saved_body = []
        for i in range(0, len(self.body)):
            saved_body.append(self.body[i])
        saved_tail = self.tail

        # Proveravamo smer kretanja zmije i shodno tome menjamo poziciju glave
        # -------------------------------------
        # Bolja preglednost koda sa x/y
        x = saved_head.x
        y = saved_head.y
        # ------------------------------------- 
        if direction == 'u':
            new_head_position = grid.itemAtPosition(x - 1, y).widget()
            self.head = Head(new_head_position, RotateDegrees.Up, self.headPicture)
        elif direction == 'd':
            new_head_position = grid.itemAtPosition(x + 1, y).widget()
            self.head = Head(new_head_position, RotateDegrees.Down, self.headPicture)
        elif direction == 'l':
            new_head_position = grid.itemAtPosition(x, y - 1).widget()
            self.head = Head(new_head_position, RotateDegrees.Left, self.headPicture)
        elif direction == 'r':
            new_head_position = grid.itemAtPosition(x, y + 1).widget()
            self.head = Head(new_head_position, RotateDegrees.Right, self.headPicture)

        # Cuvamo vrednosti opet zbog bolje preglednosti dalje
        old_degree = saved_head.degree
        new_degree = self.head.degree
        blk_type = BlockType.Body
        # Ako je zmija u prethodnom koraku presla preko hrane dodajemo novo telo iza glave.
        # A u suprotnom sve pomeramo za jedno mesto
        if self.eat == 1:
            new_body_position = grid.itemAtPosition(x, y).widget()

            if old_degree != new_degree:
                right_degree = self.body_rotation(old_degree, new_degree)
                blk_type = BlockType.CurvedBody
            else:
                right_degree = old_degree

            if blk_type == BlockType.CurvedBody:
                self.body.append(Body(new_body_position, right_degree, blk_type, self.curvedBodyPicture))
            else:
                self.body.append(Body(new_body_position, right_degree, blk_type, self.bodyPicture))
            self.eat = 0
        else:
            for i in range(0, len(self.body) - 1):
                new_body_position = grid.itemAtPosition(self.body[i + 1].x,
                                                        self.body[i + 1].y).widget()
                if self.body[i + 1].BlkType == BlockType.CurvedBody:
                    self.body[i] = Body(new_body_position, self.body[i + 1].degree, self.body[i + 1].BlkType, self.curvedBodyPicture)
                else:
                    self.body[i] = Body(new_body_position, self.body[i + 1].degree, self.body[i + 1].BlkType, self.bodyPicture)

            new_body_position = grid.itemAtPosition(x, y).widget()
            if old_degree != new_degree:
                right_degree = self.body_rotation(old_degree, new_degree)
                blk_type = BlockType.CurvedBody
            else:
                right_degree = old_degree

            if blk_type == BlockType.CurvedBody:
                self.body[len(self.body) - 1] = Body(new_body_position, right_degree, blk_type, self.curvedBodyPicture)
            else:
                self.body[len(self.body) - 1] = Body(new_body_position, right_degree, blk_type, self.bodyPicture)

            # Odredjujemo novu poziciju  repa
            new_tail_position = grid.itemAtPosition(saved_body[0].x, saved_body[0].y).widget()
            tail_degree = self.tail_rotation(saved_body, saved_head, saved_tail)
            self.tail = Tail(new_tail_position, tail_degree, self.tailPicture, self.OnMove)

            # Brisemo stari rep
            clean_block = grid.itemAtPosition(saved_tail.x, saved_tail.y).widget()
            clean_block.BType = BlockType.EmptyBlock

        self.last_move = direction

    def kill_snake(self, grid):
        block = grid.itemAtPosition(self.head.x, self.head.y).widget()
        block.BType = BlockType.EmptyBlock
        block = grid.itemAtPosition(self.tail.x, self.tail.y).widget()
        block.BType = BlockType.EmptyBlock

        for bodyPart in self.body:
            block = grid.itemAtPosition(bodyPart.x, bodyPart.y).widget()
            block.BType = BlockType.EmptyBlock
        
        self.killed = True

    @staticmethod
    def tail_rotation(saved_body, saved_head, saved_tail):
        if saved_body[0].BlkType == BlockType.CurvedBody:
            xclanak = saved_body[0].x
            yclanak = saved_body[0].y
            if len(saved_body) > 1:
                xtelo = saved_body[1].x
                ytelo = saved_body[1].y
            else:
                xtelo = saved_head.x
                ytelo = saved_head.y
            xdif = xclanak - xtelo
            ydif = yclanak - ytelo

            if xdif == 1 and ydif == 0:
                return RotateDegrees.Up
                # telo desno od clanka
            elif xdif == -1 and ydif == 0:
                return RotateDegrees.Down
                # telo ispod clanka
            elif xdif == 0 and ydif == -1:
                return RotateDegrees.Right
                # telo iznad clanka
            elif xdif == 0 and ydif == 1:
                return RotateDegrees.Left
        else:
            return saved_tail.degree

    @staticmethod
    def body_rotation(old_degree, new_degree):
        if (old_degree == RotateDegrees.Right and new_degree == RotateDegrees.Down) or \
                (old_degree == RotateDegrees.Down and new_degree == RotateDegrees.Left) or \
                (old_degree == RotateDegrees.Left and new_degree == RotateDegrees.Up) or \
                (old_degree == RotateDegrees.Up and new_degree == RotateDegrees.Right):
            return old_degree
        else:
            if old_degree + 90 > 270:
                return RotateDegrees.Right
            return old_degree + 90

    def init_snake(self, grid, player_id, snake_id):
        need_to_rotate = RotateDegrees.Right
        if player_id == 0:
            head_position = grid.itemAtPosition(0 + snake_id, 2).widget()
            body_position = grid.itemAtPosition(0 + snake_id, 1).widget()
            tail_position = grid.itemAtPosition(0 + snake_id, 0).widget()
            self.last_move = 'r'
            self.headPicture = "resources/head.png"
            self.bodyPicture = "resources/body.png"
            self.curvedBodyPicture = "resources/curvedbody.png"
            self.tailPicture = "resources/tail.png"

        elif player_id == 1:
            head_position = grid.itemAtPosition(0 + snake_id, 12).widget()
            body_position = grid.itemAtPosition(0 + snake_id, 13).widget()
            tail_position = grid.itemAtPosition(0 + snake_id, 14).widget()
            need_to_rotate = RotateDegrees.Left
            self.last_move = 'l'
            self.headPicture = "resources/head2.png"
            self.bodyPicture = "resources/body2.png"
            self.curvedBodyPicture = "resources/curvedbody2.png"
            self.tailPicture = "resources/tail2.png"

        elif player_id == 2:
            head_position = grid.itemAtPosition(14 - snake_id, 2).widget()
            body_position = grid.itemAtPosition(14 - snake_id, 1).widget()
            tail_position = grid.itemAtPosition(14 - snake_id, 0).widget()
            self.last_move = 'r'
            self.headPicture = "resources/head3.png"
            self.bodyPicture = "resources/body3.png"
            self.curvedBodyPicture = "resources/curvedbody3.png"
            self.tailPicture = "resources/tail3.png"

        else:
            head_position = grid.itemAtPosition(14 - snake_id, 12).widget()
            body_position = grid.itemAtPosition(14 - snake_id, 13).widget()
            tail_position = grid.itemAtPosition(14 - snake_id, 14).widget()
            need_to_rotate = RotateDegrees.Left
            self.last_move = 'l'
            self.headPicture = "resources/head4.png"
            self.bodyPicture = "resources/body4.png"
            self.curvedBodyPicture = "resources/curvedbody4.png"
            self.tailPicture = "resources/tail4.png"

        self.head = Head(head_position, need_to_rotate, self.headPicture)
        self.body.append(Body(body_position, need_to_rotate, BlockType.Body, self.bodyPicture))
        self.tail = Tail(tail_position, need_to_rotate, self.tailPicture, self.OnMove)

        return self

    def on_off_move(self, grid):
        if self.OnMove:
            self.OnMove = False
        else:
            self.OnMove = True
        block = grid.itemAtPosition(self.tail.x, self.tail.y).widget()
        block.OnMove = self.OnMove
