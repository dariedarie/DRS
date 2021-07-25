from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Models.Block import Block, BlockType
import random
import sys

from Models.Block import RotateDegrees


class Food(Block):
    x = 0
    y = 0
    picture = 'resources/food.png'
    deactivateFood = pyqtSignal()
    activateFood = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent.x, parent.y)
        parent.BType = BlockType.Food
        parent.RDegrees = RotateDegrees.Right