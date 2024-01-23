from turtle import Turtle
from screen import SCREEN_SIZE

class GameBoard(Turtle):
    def __init__(self):
        super().__init__()
        self.penup()
        self.hideturtle()
        self.color("green")
        self.goto(-(0.9*SCREEN_SIZE["width"]),(0.83*SCREEN_SIZE["height"]))
        self.pendown()
        self.goto(-(0.9*SCREEN_SIZE["width"]),-(0.9*SCREEN_SIZE["height"]))
        self.goto((0.9*SCREEN_SIZE["width"]),-(0.9*SCREEN_SIZE["height"]))
        self.goto((0.9*SCREEN_SIZE["width"]),(0.83*SCREEN_SIZE["height"]))
        self.goto(-(0.9*SCREEN_SIZE["width"]),(0.83*SCREEN_SIZE["height"]))
