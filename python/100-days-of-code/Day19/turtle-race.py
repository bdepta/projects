from turtle import Turtle, Screen

screen_size = {
    "width" : 640,
    "height": 480
}
start = -(screen_size["width"] - 20)
finish = screen_size["width"] - 20


def define_screen():
    screen = Screen()
    screen.screensize(screen_size["width"],screen_size["height"])
    return screen

screen = define_screen()
x = Turtle()
x.penup()
x.setpos(start, 0)


screen.exitonclick()