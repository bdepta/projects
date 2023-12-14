
#* Exercise 1 - Odd or Even
# Write a program that works out whether if a given number is an odd or even number.
# Even numbers can be divided by 2 with no remainder.
# e.g. 86 is even because 86 ÷ 2 = 43
# 43 does not have any decimal places. Therefore the division is clean.
# e.g. 59 is odd because 59 ÷ 2 = 29.5
# 29.5 is not a whole number, it has decimal places. Therefore there is a remainder of 0.5, so the division is not clean.
# The modulo is written as a percentage sign (%) in Python. It gives you the remainder after a division.
# e.g.
# 6 ÷ 2 = 3 with no remainder.
# therefore: 6 % 2 = 0
# 5 ÷ 2 = 2 x 2 + 1, remainder is 1.
# therefore: 5 % 2 = 1
# 14 ÷ 4 = 3 x 4 + 2, remainder is 2.
# therefore: 14 % 4 = 2
# Warning your output should match the Example Output format exactly, even the positions of the commas and full stops.

number = int(input("Provide number you want to check: "))
check = number % 2
if check != 0:
    print(f'This is an odd number.')
else:
    print(f'This is an even number.')

#* Exercise 2 - BMI 2.0
# Write a program that interprets the Body Mass Index (BMI) based on a user's weight and height.
# It should tell them the interpretation of their BMI based on the BMI value.
# Under 18.5 they are underweight
# Over 18.5 but below 25 they have a normal weight
# Equal to or over 25 but below 30 they are slightly overweight
# Equal to or over 30 but below 35 they are obese
# Equal to or over 35 they are clinically obese.
height = float(input("Please input your height: "))
weight = float(input("Please input your weight: "))

bmi = (weight)/(height*height)
if bmi <= 18.5:
    bmi_status = "you are underweight."
elif bmi >= 18.4 and bmi <= 24.9:
    bmi_status = "you have a normal weight."
elif bmi >= 25.0 and bmi <= 29.9:
    bmi_status = "you are slightly overweight."
elif bmi >= 30 and bmi <= 35:
    bmi_status = "you are obese."
elif bmi >= 35:
    bmi_status = "you are clinically obese."
else:
    bmi_status = "Wrong BMI calculation."

bmi = round(bmi, 3)
print(f'Your BMI is {bmi}, {bmi_status}')

#* Exercise 3 - Leap year
# Write a program that works out whether if a given year is a leap year. A normal year has 365 days, leap years have 366, with an extra day in February. The reason why we have leap years is really fascinating, this video does it more justice.
# This is how you work out whether if a particular year is a leap year.
#     - on every year that is divisible by 4 with no remainder
#     - except every year that is evenly divisible by 100 with no remainder
#     - unless the year is also divisible by 400 with no remainder
# e.g. The year 2000:
# 2000 ÷ 4 = 500 (Leap)
# 2000 ÷ 100 = 20 (Not Leap)
# 2000 ÷ 400 = 5 (Leap!)
# So the year 2000 is a leap year.
# But the year 2100 is not a leap year because:
# 2100 ÷ 4 = 525 (Leap)
# 2100 ÷ 100 = 21 (Not Leap)
# 2100 ÷ 400 = 5.25 (Not Leap)
# Warning your output should match the Example Output format exactly, including spelling an punctuation.

year = int(input("Provide year to check: "))

if year % 4 == 0:
    if year % 100 == 0:
        if year % 400 == 0:
            print(f'Leap year')
        else:
            print(f'Not leap year')
    else:
        print(f'Leap year')
else:
    print(f'Not leap year')

#TODO Exercise 4 - Pizza Order Practice
# Congratulations, you've got a job at Python Pizza! Your first job is to build an automatic pizza order program.
# Based on a user's order, work out their final bill.
# Small pizza (S): $15
# Medium pizza (M): $20
# Large pizza (L): $25
# Add pepperoni for small pizza (Y or N): +$2
# Add pepperoni for medium or large pizza (Y or N): +$3
# Add extra cheese for any size pizza (Y or N): +$1

def PizzaSize():
    bill = 0 
    size = 0
    size = input("What's pizza size you would like to order. We offer S ($15), M ($20) and L ($25)?\n")
    if size == "S":
        bill =+ 15
    if size == "M":
        bill =+ 20
    if size == "L":
        bill =+ 25
    return size, bill

def ExtraToppings(size, bill):
    if size == "S":
        addPeperoni = input("Add pepperoni for small pizza ($2)?")
        if addPeperoni == "Y" or addPeperoni == "N":
            if addPeperoni == 'Y':
                bill += 2
        else:
            print(f'Wrong input, please choose Y or N.')
            ExtraToppings(size, bill)
            
    if size == "M" or size == "L":
        addPeperoni = input("Add pepperoni for medium or large pizza ($3)?")
        if addPeperoni == "Y" or addPeperoni == "N":
            if addPeperoni == 'Y':
                bill += 3
        else:
            print(f'Wrong input, please choose Y or N.')
            ExtraToppings(size, bill)
    if size == "S" or size == "M" or size == "L":    
        addExtraCheese = input("Add extra cheese for any size pizza ($1)?")
        if addExtraCheese == "Y" or addExtraCheese == "N":
            if addExtraCheese == 'Y':
                bill += 1
        else:
            print(f'Wrong input, please choose Y or N.')
            ExtraToppings(size, bill)
    else:
        print(f'Something went wrong. Please start again.')
        exit()
    
    return bill

print(f'Thank you for choosing Python Pizza Deliveries!')
bill = PizzaSize()
final_bill = ExtraToppings(bill[0], bill[1])
print(f'Your final bill is: ${final_bill}')

#* Exercise 5 - Love Calculator
# You are going to write a program that tests the compatibility between two people.
# To work out the love score between two people:
#   1. Take both people's names and check for the number of times the letters in the word TRUE occurs.
#   2. Then check for the number of times the letters in the word LOVE occurs.
#   3. Then combine these numbers to make a 2 digit number.
# For Love Scores less than 10 or greater than 90, the message should be:
# "Your score is *x*, you go together like coke and mentos."
# For Love Scores between 40 and 50, the message should be:
# "Your score is *y*, you are alright together."
# Otherwise, the message will just be their score. e.g.:
# "Your score is *z*."
# e.g.
# name1 = "Angela Yu"
# name2 = "Jack Bauer"
# T occurs 0 times
# R occurs 1 time
# U occurs 2 times
# E occurs 2 times
# Total = 5
# L occurs 1 time
# O occurs 0 times
# V occurs 0 times
# E occurs 2 times
# Total = 3
# Love Score = 53
# Print: "Your score is 53."

name1 = input("Please provide first name: ")
name2 = input("Please provide second name: ")
name1 = name1.lower()
name2 = name2.lower()
loveScore1 = 0
loveScore2 = 0
loveCheck1 = "true"
loveCheck2 = "love"
for i in loveCheck1:
	x = name1.count(i)
	loveScore1 += int(x)
	x = name2.count(i)
	loveScore1 += int(x)
for j in loveCheck2:
	y = name1.count(j)
	loveScore2 += int(y)
	y = name2.count(j)
	loveScore2 += int(y)

loveResult = str(loveScore1) + str(loveScore2)
loveResult = int(loveResult)

if loveResult < 10 or loveResult > 90:
	print(f'Your score is {loveResult}, you go together like coke and mentos.')
elif loveResult >= 40 and loveResult <=50:
	print(f'Your score is {loveResult}, you are alright together.')
else:
	print(f'Your score is {loveResult}.')