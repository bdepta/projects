
#* Exercise 1
# Write a program that adds the digits in a 2 digit number. e.g. if the input was 35, then the output should be 3 + 5 = 8
# Warning. Do not change the code on line 1. Your program should work for different inputs. e.g. any two-digit number.
# The last line of your program should print the result.
digit = input("Provide two your number: ")
res = 0
for i in digit:
    res+=int(i)
print (res)

#* Exercise 2
# Write a program that calculates the Body Mass Index (BMI) from a user's weight and height.
# The BMI is a measure of someone's weight taking into account their height. e.g. If a tall person and a short person both weigh the same amount, the short person is usually more overweight.
# The BMI is calculated by dividing a person's weight (in kg) by the square of their height (in m):
weight = float(input("Please input your weight: "))
height = float(input("Please input your height: "))
bmi = (weight)/(height*height)
if bmi < 18.4:
    bmi_status = "Underweight"
elif bmi > 18.4 and bmi < 24.9:
    bmi_status = "Normal"
elif bmi > 25.0 and bmi < 29.9:
    bmi_status = "Overweight"
elif bmi > 30:
    bmi_status = "Obese"
else:
    bmi_status = "Wrong BMI calculation"

bmi = round(bmi, 3)
print(f'Your BMI is : {bmi}\nWhich means that you are {bmi_status}')
#* Exercise 3
# I was reading this article by Tim Urban - Your Life in Weeks and realized just how little time we actually have.
# Create a program using maths and f-Strings that tells us how many weeks we have left, if we live until 90 years old.
# It will take your current age as the input and output a message with our time left in this format:
# You have x weeks left.
# Where x is replaced with the actual calculated number of weeks the input age has left until age 90.
# Warning your output should match the Example Output format exactly, even the positions of the commas and full stops.
age = input("What's your current age? ")
yearsLeft = 90 - int(age)
weeksLeft = int(yearsLeft) * 52
print(f'Assuming that you will live until 90 years old. You have {weeksLeft} weeks left.')
