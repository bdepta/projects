from turtle import Turtle
from screen import SCREEN_SIZE
import os

ALIGN = 'center'
FONT = ('Courier New', 16, 'normal')

PATH = "high_score.txt"

class ScoreBoard(Turtle):
    def __init__(self):
        super().__init__()
        self.hideturtle()
        self.penup()
        self.goto(0,(SCREEN_SIZE["height"]-(0.15*SCREEN_SIZE["height"])))
        self.color("white")
        self.score = 0
        self.read_file()
        self.display_score()
    def read_file(self):
        if os.path.isfile(PATH) == False:
            with open(PATH, mode="w") as file:
                file.write("0")
        with open(PATH) as file:
            self.high_score = int(file.read())
        
    def reset_game(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open(PATH, mode="w") as file:
                file.write(str(self.high_score))
        self.score = 0
        self.display_score()
    
    # def game_over(self):
    #     self.home()
    #     self.write("GAME OVER", align=ALIGN, font=FONT)
    
    def display_score(self):
        self.clear()
        self.write(f"Score: {self.score} High Score: {self.high_score}", move= False,  align=ALIGN, font=FONT)
    
    def add_point(self):
        self.score += 1
        self.display_score()