
# # * Exercise 1 - Fix code samples

# # # Describe Problem
# # def my_function():
# #   # for i in range(1, 20):
# #   for i in range(1,21):  
# #     if i == 20:
# #       print("You got it")
# # my_function()

# # # Reproduce the Bug
# # from random import randint
# # dice_imgs = ["❶", "❷", "❸", "❹", "❺", "❻"]
# # dice_num = randint(0, 5)
# # # dice_num = randint(6, 12)
# # print(dice_imgs[dice_num])

# # # Play Computer
# # year = int(input("What's your year of birth?"))
# # if year > 1980 and year < 1994:
# #   print("You are a millenial.")
# # elif year >= 1994:
# #   print("You are a Gen Z.")

# # # Fix the Errors
# # age = int(input("How old are you?"))
# # if age > 18:
# #   print(f"You can drive at age {age}.")

# # #Print is Your Friend
# # pages = 0
# # word_per_page = 0
# # pages = int(input("Number of pages: "))
# # word_per_page = int(input("Number of words per page: "))
# # total_words = pages * word_per_page
# # print(total_words)

# # #Use a Debugger
# # def mutate(a_list):
# #   b_list = []
# #   for item in a_list:
# #     new_item = item * 2
# #     b_list.append(new_item)
# #   print(b_list)

# # mutate([1,2,3,5,8,13])

# # * Exercise 2 -  DEBUGGING ODD OR EVEN
# # Read this the code in main.py
# # Spot the problems 🐞.
# # Modify the code to fix the program.
# # Fix the code so that it works and passes the tests when you submit.

# # Hint
# # Review the previous lesson and go through the 10 steps to tackle these debugging problems.

# number = int(input()) # Which number do you want to check?

# if number % 2 == 0:
#   print("This is an even number.")
# else:
#   print("This is an odd number.")

# # * Exercise 3 -  DEBUGGING LEAP YEAR

# # Read this the code in main.py
# # Spot the problems 🐞.
# # Modify the code to fix the program.
# # No shortcuts - don't copy-paste to replace the code entirely with a working solution.
# # Fix the code so that it works and when you hit submit it should pass all the tests.
  

# year = int(input())

# if year % 4 == 0:
#   if year % 100 == 0:
#     if year % 400 == 0:
#       print("Leap year.")
#     else:
#       print("Not leap year.")
#   else:
#     print("Leap year.")
# else:
#   print("Not leap year.")


# * Exercise 4 -  DEBUGGING FIZZBUZZ
  
# Read this the code in main.py
# Spot the problems 🐞.
# Modify the code to fix the program.
# No shortcuts - don't copy-paste to replace the code entirely with a working solution.
# The code needs to print the solution to the FizzBuzz game.

# Your program should print each number from 1 to x where x is the input number.

# However when the number is divisible by 3 then instead of printing the number it should print "Fizz".

# When the number is divisible by 5, then instead of printing the number it should print "Buzz".

# And if the number is divisible by both 3 and 5 e.g. 15 then instead of the number it should print "FizzBuzz".

# Hint
# There is more than one fix required.

target = int(input())
for number in range(1, target + 1):
  if number % 3 == 0 and number % 5 == 0:
    print("FizzBuzz")
  elif number % 3 == 0:
    print("Fizz")
  elif number % 5 == 0:
    print("Buzz")
  else:
    print([number])