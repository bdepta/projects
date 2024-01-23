#####Turtle Intro######

import turtle as t
import random
# timmy_the_turtle = t.Turtle()
# timmy_the_turtle.shape("turtle")
# timmy_the_turtle.color("red")
# timmy_the_turtle.forward(100)
# timmy_the_turtle.backward(200)
# timmy_the_turtle.right(90)
# timmy_the_turtle.left(180)
# timmy_the_turtle.setheading(0)


######## Challenge 1 - Draw a Square ############
# timmy_the_turtle = t.Turtle()
# timmy_the_turtle.shape("arrow")
# timmy_the_turtle.color("red")
# for _ in range(4):
#     timmy_the_turtle.forward(100)
#     timmy_the_turtle.right(90)

########### Challenge 2 - Draw a Dashed Line ########
# tim = t.Turtle()
# tim.shape("arrow")
# for _ in range(15):
#     tim.pendown()
#     tim.forward(10)
#     tim.penup()
#     tim.forward(10)

########### Challenge 3 - Draw Shapes ########
# tim = t.Turtle()
# tim.shape("turtle")
# colors = ["red","blue","green","orange","yellow","purple","black","silver"]
# angles = 3

# for i in colors:
#     tim.color(i)
#     shape = 360 / angles
#     for _ in range(angles):
#         tim.right(shape)
#         tim.forward(200)
#     angles += 1
########### Challenge 4 - Random Walk ########

# t.colormode(255)

# def random_color():
#     r = random.randint(0,255)
#     g = random.randint(0,255)
#     b = random.randint(0,255)
#     color = (r,g,b)
#     return color
# def random_walk():
#     colors = random_color()
#     direction = [0,90,180,270]
#     tim.color(colors)
#     random_direction = random.choice(direction)
#     tim.seth(random_direction)
#     tim.forward(50)

# tim = t.Turtle()
# tim.speed(10)
# tim.pensize(20)
# for _ in range(200):
#     random_walk()

########### Challenge 5 - Spirograph ########
tim = t.Turtle()
tim.speed("fastest")
tim.pensize(2)
t.colormode(255)
def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    color = (r, g, b)
    return color

angle = 0

while angle < 360:
    tim.color(random_color())
    tim.seth(angle)
    tim.circle(100)
    angle += 5

screen = t.Screen()
screen.exitonclick()