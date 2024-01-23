from turtle import Turtle
from screen import SCREEN_SIZE
import random

class Ball(Turtle):
    def __init__(self):
        super().__init__()
        
           
        
    def reset_ball(self, counter):
        self.shape("circle")
        self.color("white")
        self.penup()
        self.shapesize(stretch_len=1,stretch_wid=1)
        self.goto(0,0)
        self.move_speed= 0.1
        self.x_move = 10
        self.y_move = random.randint(1,10)
        self.rand_y = [-self.y_move , self.y_move]
        self.y_move = random.choice(self.rand_y)
        if counter%2 == 0:
            self.x_move = self.x_move
        else:
            self.x_move = -self.x_move
    def accelerate_ball(self):
        self.move_speed -= (0.4*self.move_speed)
    
    def ball_move(self):
        new_x = self.xcor() + self.x_move
        new_y = self.ycor() + self.y_move
        self.goto(new_x, new_y)
    
    def bounce(self):
        self.y_move *= -1
    def bounce_x(self):
        self.x_move *= -1
