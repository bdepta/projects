from screen import ScreenDefinition, SCREEN_SIZE
from ball import Ball
from scoreboard import ScoreBoard
from paddle import Paddle
import time

field_edges_y = [(-0.89*SCREEN_SIZE["height"]),(0.79*SCREEN_SIZE["height"])]
field_edges_x = [(-(0.975*SCREEN_SIZE["width"])),(0.96*SCREEN_SIZE["width"])]
game_is_on = True
screen = ScreenDefinition()
ball = Ball()
scoreboard = ScoreBoard()
counter = 0

left_paddle = Paddle()
right_paddle = Paddle()
left_paddle.define_paddle(0)
right_paddle.define_paddle(1)
screen.screen_listen()
screen.screen_onkey(key="Up", function=right_paddle.up)
screen.screen_onkey(key="Down", function=right_paddle.down)
screen.screen_onkey(key="w", function=left_paddle.up)
screen.screen_onkey(key="s", function=left_paddle.down)

ball.reset_ball(counter)
while game_is_on:
    screen.screen_update()
    time.sleep(ball.move_speed)
    ball.ball_move()
    
    if ball.ycor() < field_edges_y[0] or ball.ycor() > field_edges_y[1]:
        ball.bounce()
    if ball.distance(right_paddle) < 50 and ball.xcor() > (SCREEN_SIZE["width"]-(0.15*SCREEN_SIZE["width"])) or ball.distance(left_paddle) < 39 and ball.xcor() > (-SCREEN_SIZE["width"]-(0.10*SCREEN_SIZE["width"])):
        ball.bounce_x()
        ball.accelerate_ball()
    if ball.xcor() < field_edges_x[0]:
        scoreboard.add_point(position=1)
        counter += 1
        ball.reset_ball(counter)
    if ball.xcor() > field_edges_x[1]:
        scoreboard.add_point(position=0)
        counter += 1
        ball.reset_ball(counter)
screen.exit_on_click()