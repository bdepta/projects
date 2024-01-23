from turtle import Turtle
from screen import SCREEN_SIZE

ALIGN = 'left'
FONT = ('Courier New', 32, 'normal')

class ScoreBoard(Turtle):
    def __init__(self):
        super().__init__()
        self.score = [0,0]
        self.display_score()
        self.create_game_area()
    def display_score(self):
        self.hideturtle()
        self.penup()
        self.pensize(width=5)
        self.goto((-SCREEN_SIZE["width"]+(0.74*SCREEN_SIZE["width"])),(SCREEN_SIZE["height"]-(0.15*SCREEN_SIZE["height"])))
        self.color("white")
        self.write(f"{self.score[0]}\t{self.score[1]}", move= False,  align=ALIGN, font=FONT)
    def add_point(self, position):
        self.score[position] += 1
        self.clear()
        self.display_score()
        self.create_game_area()
    def create_game_area(self):
        self.goto(-(0.975*SCREEN_SIZE["width"]),(0.83*SCREEN_SIZE["height"]))
        self.pendown()
        self.goto(-(0.975*SCREEN_SIZE["width"]),-(0.94*SCREEN_SIZE["height"]))
        self.goto((0.96*SCREEN_SIZE["width"]),-(0.94*SCREEN_SIZE["height"]))
        self.goto((0.96*SCREEN_SIZE["width"]),(0.83*SCREEN_SIZE["height"]))
        self.goto(-(0.975*SCREEN_SIZE["width"]),(0.83*SCREEN_SIZE["height"]))
        self.penup()
        self.middle_section()
    def middle_section(self):    
        self.goto(0, -(0.15*SCREEN_SIZE["width"]))
        self.pendown()
        self.circle((0.16*SCREEN_SIZE["width"]))
        self.penup()
        self.goto(0,(-0.94*SCREEN_SIZE["height"]))
        self.pendown()
        self.goto(0, 0.83*SCREEN_SIZE["height"])
        
