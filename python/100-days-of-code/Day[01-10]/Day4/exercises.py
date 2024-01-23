
# * Exercise 1 - Head or Tail
# You are going to write a virtual coin toss program. It will randomly tell the user "Heads" or "Tails".
# Important, the first letter should be capitalized and spelt exactly like in the example e.g. "Heads", not "heads".
# There are many ways of doing this. But to practice what we learnt in the last lesson, you should generate a random number, either 0 or 1. Then use that number to print out "Heads" or "Tails".
# e.g. 1 means Heads 0 means Tails
import random

result = random.randint(0,1)

if result == 0:
    print(f"Tails")
if result == 1:
    print(f"Heads")

# * Exercise 2 - Banker Roulette
# You are going to write a program that will select a random name from a list of names. The person selected will have to pay for everybody's food bill.
# Important: You are not allowed to use the choice() function.
# Line 1 splits the string names_string into individual names and puts them inside a List called names. For this to work, you must enter all the names as names followed by comma then space. e.g. name, name, name
# NOTE: Don't worry about getting hold of the input(), we've done the work behind the scenes to import everything.
# HINT: Assume that names looks like this: input: x, y, z, names = ["x", "y", "z"]

names_string = input("Who ate the meal?\n")
names = names_string.split(", ")
num_items = len(names)
index = random.randint(0,num_items -1)
print(f'{names[index]} is going to buy the meal today!')

# * Exercise 3 - Treasure Map
# You are going to write a program that will mark a spot on a map with an X.
# First, your program must take the user input and convert it to a usable format.
# Next, you need to use that input to update your nested list with an "X". Remember that your nested list map actually looks like this:

line1 = ["⬜️","️⬜️","️⬜️"]
line2 = ["⬜️","⬜️","️⬜️"]
line3 = ["⬜️️","⬜️️","⬜️️"]
print(f"{line1}\n{line2}\n{line3}")
position = str(input("Where do you want to hide your treasure ?\n"))
if position[0] == "A":
    x = 0
elif position[0] == "B":
    x = 1
elif position[0] == "C":
    x = 2
else:
    print("You are outside of the map. Please choose position which exist on the map.")
    exit()
if int(position[1]) <= 3:
    y = int(position[1]) - 1
else:
    print("You are outside of the map. Please choose position which exist on the map.")
    exit()
treasureMap = [line1,line2,line3]
treasureMap[y][x] = "X" 
print(f'{treasureMap[0]}\n{treasureMap[1]}\n{treasureMap[2]}')