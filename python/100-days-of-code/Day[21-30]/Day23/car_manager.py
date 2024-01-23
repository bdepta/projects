from turtle import Turtle
import random
COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]
STARTING_MOVE_DISTANCE = 5
MOVE_INCREMENT = 5


class CarManager():
    def __init__(self):
        self.all_cars = []
        self.move_speed = STARTING_MOVE_DISTANCE
    
    def create_car(self):
        random_chance = random.randint(1,8)
        if random_chance == 1:
            t = Turtle()
            t.shape("square")
            t.shapesize(stretch_len=2,stretch_wid=1)
            t.penup()
            t.color(random.choice(COLORS))
            rand_y = random.randint(-250, 270)
            t.goto(300, rand_y)
            self.all_cars.append(t)

    def move_car(self):
        for i in self.all_cars:
            new_x = i.xcor() - self.move_speed
            i.setx(new_x)
    
    def accelerate_car(self):
        self.move_speed += MOVE_INCREMENT
