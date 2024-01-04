
#* Exercise 1
# Day 1 - Python Print Function
# The function is declared like this:
# print('what to print')
print("Day 1 - Python Print Function\nThe function is declared like this:\nprint('what to print')")
#* Exercise 2
# Fix the code below 👇
print("Day 1 - String Manipulation")
print('String Concatenation is done with the "+" sign.')
print('e.g. print("Hello " + "world")')
print("New lines can be created with a backslash and n.")
#* Exercise 3
# Write a program that calculates and outputs the number of characters in any name. 
# The automated tests will try out lots of different names as the input.
# Your code should work for any name.
name = input("What is your name?\n")
print("Hello " + name + "! Your name has " + str(len(name)) + " characters.")
#* Exercise 4
# This program takes two inputs. The first input is stored in a variable called a. The second input is stored in a variable called b.
# Write a program that switches the values stored in the variables a and b.
# Warning . You don't need to print anything. The print statement is already in the template code. However, your program should work for different inputs. e.g. any value of a and b.
a = input("Provide first value: ")
b = input("Provide second value: ")

def SwitchValues(a, b):
    # introduce supporting variable, and save variable a to variable c
    c = a
    # pass value from variable b to variable a
    a = b
    # pass value from supporting variable c to variable b
    b = c
    return a, b
res = SwitchValues(a,b)
a = res[0]
b = res[1]
print(a , b)
