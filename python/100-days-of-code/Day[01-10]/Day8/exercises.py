
# * Exercise 1 - Paint Area Calculator
# You are painting a wall. The instructions on the paint can says that 1 can of paint can cover 5 square meters of wall. Given a random height and width of wall, calculate how many cans of paint you'll need to buy.
# number of cans = (wall height x wall width) ÷ coverage per can.
# e.g. Height = 2, Width = 4, Coverage = 5
# number of cans = (2 \* 4) / 5
#                = 1.6
# But because you can't buy 0.6 of a can of paint, the result should be rounded up to 2 cans.
import math
def PaintCalc(height, width, cover):
    numberOfCans = ((height * width) / cover)
    numberOfCans = math.ceil(numberOfCans)
    print(f" You will need {numberOfCans} cans of paint")
testH = int(input()) # Height of wall (m)
testW = int(input()) # Width of wall (m)
coverage = 5
PaintCalc(height=testH, width=testW, cover=coverage)
# TODO Exercise 2 - Prime numbers
# Prime numbers are numbers that can only be cleanly divided by themselves and 1.
# You need to write a function that checks whether if the number passed into it is a prime number or not.
# e.g. 2 is a prime number because it's only divisible by 1 and 2.
# But 4 is not a prime number because you can divide it by 1, 2 or 4.

def CheckIfPrime(number):
    counter = 0
    for i in range(1,number+1):
        if number % i == 0:
            counter += 1
    if counter == 2:
        print("It's a prime number.")
    else:
        print(f"It's not a prime number.")

n = int(input())
CheckIfPrime(number=n)