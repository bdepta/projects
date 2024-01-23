from snake import Snake
from screen import ScreenDefinition
import time

screen = ScreenDefinition()
game_is_on = True
snake = Snake()
screen.screen_listen()
screen.screen_onkey(key="Up", function=snake.up)
screen.screen_onkey(key="Down", function=snake.down)
screen.screen_onkey(key="Left", function=snake.left)
screen.screen_onkey(key="Right", function=snake.right)
while game_is_on:
    screen.screen_update()
    time.sleep(0.1)
    snake.move()

screen.exit_on_click()