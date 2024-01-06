from turtle import Turtle
from screen import SCREEN_SIZE

ALIGN = 'center'
FONT = ('Courier New', 16, 'normal')

class ScoreBoard(Turtle):
    def __init__(self):
        super().__init__()
        self.hideturtle()
        self.penup()
        self.goto(0,(SCREEN_SIZE["height"]-(0.15*SCREEN_SIZE["height"])))
        self.color("white")
        self.score = 0
        self.display_score()
    
    def game_over(self):
        self.home()
        self.write("GAME OVER", align=ALIGN, font=FONT)
    
    def display_score(self):
        self.write(f"Score: {self.score}", move= False,  align=ALIGN, font=FONT)
    
    def add_point(self):
        self.score += 1
        self.clear()
        self.display_score()