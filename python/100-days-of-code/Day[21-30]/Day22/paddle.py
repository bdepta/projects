from turtle import Turtle
from screen import SCREEN_SIZE

DIRECTIONS = {
    "Up": 90,
    "Down": 270,
    "Left": 180,
    "Right": 0
}

MOVE_DISTANCE = 0.1*SCREEN_SIZE["height"]

PADDLE_COORDINATES = [((-SCREEN_SIZE["width"]+(0.08*SCREEN_SIZE["width"])),0),((SCREEN_SIZE["width"]-(0.10*SCREEN_SIZE["width"])),0)]

class Paddle(Turtle):
    def __init__(self):
        super().__init__()
    def define_paddle(self, counter):
        self.color("white")
        self.shape("square")
        self.shapesize(stretch_len=3,stretch_wid=1)
        self.penup()
        self.speed("fastest")
        self.seth(DIRECTIONS["Up"])
        self.goto(PADDLE_COORDINATES[counter])
    def up (self):
        if self.ycor() != 7*MOVE_DISTANCE:
            self.seth(DIRECTIONS["Up"])
            self.paddle_move()
    def down (self):
        if self.ycor() != 8*(-MOVE_DISTANCE):
            self.seth(DIRECTIONS["Down"])
            self.paddle_move()
    def paddle_move(self):
        self.fd(MOVE_DISTANCE)
            
