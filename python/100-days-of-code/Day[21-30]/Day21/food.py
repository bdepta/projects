from turtle import Turtle
from screen import SCREEN_SIZE
import random


class Food(Turtle):
    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.penup()
        self.shapesize(stretch_len=0.75,stretch_wid=0.75)
        self.color("green")
        self.speed("fastest")
        self.refresh()

    def refresh(self):
        random_x = random.randint((-1*SCREEN_SIZE["width"]+(0.20*SCREEN_SIZE["width"])),SCREEN_SIZE["width"]-(0.20*SCREEN_SIZE["width"]))
        random_y = random.randint((-1*SCREEN_SIZE["height"]+(0.20*SCREEN_SIZE["height"])),SCREEN_SIZE["height"]-(0.20*SCREEN_SIZE["height"]))
        self.goto(random_x, random_y)