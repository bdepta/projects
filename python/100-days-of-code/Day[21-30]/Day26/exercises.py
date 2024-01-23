
#* Exercise 1

# You are going to write a List Comprehension to create a new list called squared_numbers. This new list should contain every number in the list numbers but each number should be squared.

# e.g. 4 * 4 = 16

# 4 squared equals 16.

# DO NOT modify the List numbers directly. Try to use List Comprehension instead of a Loop.
# numbers = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
# squared_numbers = [n*n for n in numbers]
#* Exercise 2
# In this list comprehension exercise you will practice using list comprehension to filter out the even numbers from a series of numbers.

# First, use list comprehension to convert the list_of_strings to a list of integers.

# Then use list comprehension again to create a new list called result. This new list should only contain the even numbers from the list numbers.

# Again, try to use Python's List Comprehension instead of a Loop.
# list_of_strings = input().split(',')
# list_of_number = [n for n in list_of_strings]
# result = [int(i) for i in list_of_number if int(i)%2 ==0 ]
# print(list_of_number)
# print(result)

#* Exercise 3

# file1 = "./file1.txt"
# file2 = "./file2.txt"


# with open(file1, mode="r") as input1:
#     numbers1 = [int(i) for i in input1.readlines()]
# with open(file2, mode="r") as input2:
#     numbers2 = [int(i) for i in input2.readlines()]

# result = [n for n in numbers2 if n in numbers1]

# print(numbers1)
# print(numbers2)
# print(result)

#* Exercise 4
# You are going to use Dictionary Comprehension to create a dictionary called result that takes each word in the given sentence and calculates the number of letters in each word.

# Try Googling to find out how to convert a sentence into a list of words.

# Do NOT Create a dictionary directly. Try to use Dictionary Comprehension instead of a Loop.

# sentence = input().split(' ')
# result = {item:len(item) for item in sentence}

# print(result)

#* Exercise 5
# You are going to use Dictionary Comprehension to create a dictionary called weather_f that takes each temperature in degrees Celsius and converts it into degrees Fahrenheit.

# To convert temp_c into temp_f use this formula:

# (temp_c * 9/5) + 32 = temp_f

weather_c = eval(input())
weather_f = { key:((value * 9/5) + 32) for (key,value) in weather_c.items()}
print(weather_f)