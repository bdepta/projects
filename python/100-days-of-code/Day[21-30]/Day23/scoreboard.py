from turtle import Turtle
FONT = ("Courier", 24, "normal")


class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()
        self.hideturtle()
        self.penup()
        self.goto(-290,260)
        self.color("black")
        self.current_level = 1
        self.display_score()
    def display_score(self):
        self.write(f"Level: {self.current_level}", move= False,  align="left", font=FONT)
    def add_point(self):
        self.current_level += 1
        self.clear()
        self.display_score()
    def game_over(self):
        self.clear()
        self.display_score()
        t = Turtle()
        t.hideturtle()
        t.penup()
        t.goto(-100,0)
        t.write(f"Game Over", move= False,  align="left", font=FONT)
