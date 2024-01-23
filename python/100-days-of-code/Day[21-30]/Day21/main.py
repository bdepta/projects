from snake import Snake
from screen import ScreenDefinition, SCREEN_SIZE
from food import Food
from scoreboard import ScoreBoard
from gameboard import GameBoard
import time


screen = ScreenDefinition()
game_is_on = True
snake = Snake()
food = Food()
score = ScoreBoard()
gameboard = GameBoard()
screen.screen_listen()
screen.screen_onkey(key="Up", function=snake.up)
screen.screen_onkey(key="Down", function=snake.down)
screen.screen_onkey(key="Left", function=snake.left)
screen.screen_onkey(key="Right", function=snake.right)
while game_is_on:
    screen.screen_update()
    time.sleep(0.1)
    snake.move()
    if snake.snake[0].distance(food) < 15:
        food.refresh()
        snake.extend()
        score.add_point()
    if snake.snake[0].xcor() > (0.9*SCREEN_SIZE["width"]) or snake.snake[0].xcor() < -(0.9*SCREEN_SIZE["width"]) or snake.snake[0].ycor() > (0.83*SCREEN_SIZE["height"]) or snake.snake[0].ycor() < -(0.9*SCREEN_SIZE["height"]):
        game_is_on = False
        score.game_over()
    for segment in snake.snake[1:]:
        if snake.snake[0].distance(segment) < 10:
            game_is_on = False
            score.game_over()
screen.exit_on_click()