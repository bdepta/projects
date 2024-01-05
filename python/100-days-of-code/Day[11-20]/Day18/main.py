###This code will not work in repl.it as there is no access to the colorgram package here.###
##We talk about this in the video tutorials##
import colorgram, random
import turtle as t

tim = t.Turtle()
tim.speed("fastest")
t.shape("circle")
t.colormode(255)
t.pensize(20)

def random_color():
    rgb_tuples = []
    colors = colorgram.extract('image.jpg', 30)
    for color in colors:
        red = color.rgb.r
        green = color.rgb.g
        blue = color.rgb.b
        my_tuple = (red,green,blue)
        rgb_tuples.append(my_tuple)
    return random.choice(rgb_tuples)
    
def move_forward():
    t.color(random_color())
    t.pendown()
    t.forward(0)
    t.penup()
    t.forward(50)
    
def move_up(counter):
    t.home()
    t.setheading(90)
    t.forward(50*counter)
    t.setheading(0)

counter = 1
for _ in range(0,9):
    for _ in range(0,9):
        move_forward()
    move_up(counter)
    counter += 1
t.home()


screen = t.Screen()
screen.exitonclick()