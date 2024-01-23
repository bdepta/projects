import turtle
import csv
from state import State as s
screen = turtle.Screen()
screen.title("U.S. States Game")
image = "./blank_states_img.gif"
screen.addshape(image)
turtle.shape(image)

us_states = []
coordinates = []

with open ('50_states.csv', newline='') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',')
    for state in csv_reader:
        my_tuple = (state[1],state[2])
        coordinates.append(my_tuple)
        us_states.append(state[0])


state_coordinates_dict = {state: {"X": x, "Y": y} for state, (x,y) in zip(us_states, coordinates)}


game_is_on = True
correctly_guessed = 0
lives = 7
while game_is_on:
    answer_state = screen.textinput(title=f"{correctly_guessed}/50 States Correct", prompt=f"What's another state's name? Chances left: {lives}")
    tmp = correctly_guessed
    for key in state_coordinates_dict.keys():
        if answer_state.lower() == key.lower():
            t = s()
            t.move_state(key,int(state_coordinates_dict[key]["X"]),int(state_coordinates_dict[key]["Y"]))
            correctly_guessed += 1
    try:
        del state_coordinates_dict[answer_state]
    except:
        print("No such item in the dictionary.")
    if correctly_guessed == tmp:
        lives -= 1
    if lives == 0 or len(state_coordinates_dict) == 0:
        game_is_on=False


screen.exitonclick()