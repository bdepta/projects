from turtle import Turtle
ALIGN = 'center'
FONT = ('Courier New', 6, 'normal')
class State(Turtle):
    def __init__(self):
        super().__init__()
        self.penup()
        self.hideturtle()
    
    def move_state(self, name, x_pos, y_pos):
        self.goto(x_pos, y_pos)
        self.write(f"{name}", move= False,  align=ALIGN, font=FONT)