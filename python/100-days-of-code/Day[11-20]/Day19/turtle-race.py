from turtle import Turtle, Screen
import random

screen_size = {
    "width" : 640,
    "height": 480
}
start = -(screen_size["width"] - 50)
finish = screen_size["width"] - 50
colors = ["red", "orange", "yellow", "green", "blue", "purple"]
turtles = []
is_race_on = False
def define_screen():
    screen = Screen()
    screen.screensize(screen_size["width"],screen_size["height"])
    return screen

screen = define_screen()
user_bet = screen.textinput(title="Make your bet", prompt="Which turtle will win the race? Enter a color.").lower()
pos_y = []
step = ((2 * screen_size["height"] ) / len(colors)) 
pos_y_tmp = screen_size["height"] - (int(step) / 2)

for _ in range(-screen_size["height"],screen_size["height"], int(step)):   
    pos_y.append(int(pos_y_tmp))
    pos_y_tmp = pos_y_tmp - ((2 * screen_size["height"] ) / len(colors)) 


for _ in range(6):
    
    i = Turtle(shape="turtle")
    i.color(colors[_])
    i.shapesize(2.5, 2.5, 2.5)
    i.penup()
    i.setpos(start, pos_y[_])
    turtles.append(i)

if user_bet:
    is_race_on = True

while is_race_on:

    for turtle in turtles:
        if turtle.xcor() > finish:
            is_race_on = False
            if user_bet == turtle.pencolor():
                screen.title(f"That's the end of race. Turtle {turtle.pencolor()} won the race. You won.")
            else:
                screen.title(f"That's the end of race. Turtle {turtle.pencolor()} won the race. You lost.")                
        else:
            rand_distance = random.randint(0,30)
            turtle.fd(rand_distance)
            


screen.exitonclick()