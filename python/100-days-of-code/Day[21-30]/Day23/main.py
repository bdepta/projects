import time
from turtle import Screen
from player import Player, FINISH_LINE_Y, STARTING_POSITION
from car_manager import CarManager
from scoreboard import Scoreboard

screen = Screen()
screen.setup(width=600, height=600)
screen.title("Awesome Bumpy Road")
screen.tracer(0)
player = Player()
score = Scoreboard()
screen.listen()
screen.onkey(player.move, "Up")
screen.onkeypress(player.move, "Up")
car_manager = CarManager()
game_is_on = True
while game_is_on:
    time.sleep(0.1)
    car_manager.create_car()
    car_manager.move_car()
    screen.update()
    if player.ycor() > FINISH_LINE_Y:
        score.add_point()
        car_manager.accelerate_car()
        player.reset_player()
    for car in car_manager.all_cars:
        if player.distance(car) < 20:
            game_is_on = False
            score.game_over()
screen.exitonclick()