from turtle import Turtle

MOVE_DISTANCE = 20
DIRECTIONS = {
    "Up": 90,
    "Down": 270,
    "Left": 180,
    "Right": 0
}

class Snake:
    def __init__(self):
        self.snake = []
        self.define()
    def define(self):
        new_snake_segment = 0
        for i in range(3):
            i = Turtle(shape="square")
            i.color("white")
            i.penup()
            i.setx(-20*new_snake_segment)
            new_snake_segment += 1
            self.snake.append(i)
        return self.snake
    
    def up (self):
        if self.snake[0].heading() != DIRECTIONS["Down"]:
            self.snake[0].seth(DIRECTIONS["Up"])
    def down (self):
        if self.snake[0].heading() != DIRECTIONS["Up"]:
            self.snake[0].seth(DIRECTIONS["Down"])
    def left (self):
        if self.snake[0].heading() != DIRECTIONS["Right"]:
            self.snake[0].seth(DIRECTIONS["Left"])
    def right (self):
        if self.snake[0].heading() != DIRECTIONS["Left"]:
            self.snake[0].seth(DIRECTIONS["Right"])
    

    def move(self):
        for segment_number in range(len(self.snake) -1, 0 , -1):
            self.snake[segment_number].goto(self.snake[segment_number-1].xcor(),self.snake[segment_number-1].ycor())
        self.snake[0].fd(MOVE_DISTANCE)
