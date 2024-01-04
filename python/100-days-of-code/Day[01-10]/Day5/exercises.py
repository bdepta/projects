
# * Exercise 1 - Average Height
# You are going to write a program that calculates the average student height from a List of heights.
# e.g. student_heights = [180, 124, 165, 173, 189, 169, 146]
# The average height can be calculated by adding all the heights together and dividing by the total number of heights.
# e.g.
# 180 + 124 + 165 + 173 + 189 + 169 + 146 = 1146
# There are a total of 7 heights in student_heights
# 1146 ÷ 7 = 163.71428571428572
# Average height rounded to the nearest whole number = 164
# Important You should not use the sum() or len() functions in your answer. You should try to replicate their functionality using what you have learnt about for loops.
studentsHeightInput = input("Provide heights of all student separated with space. ")
studentsHeightInput = studentsHeightInput.split(" ")
studentsHeight = 0
numberOfStudents = 0
for students in studentsHeightInput:
    numberOfStudents += 1
for i in studentsHeightInput:
    studentsHeight += int(i)

averageHeight = round( studentsHeight / numberOfStudents )
print(f'total height = {studentsHeight}')
print(f'number of students = {numberOfStudents}')
print(f'average height = {(averageHeight)}')
# * Exercise 2 - High Score
# You are going to write a program that calculates the highest score from a List of scores.
# e.g. student_scores = [78, 65, 89, 86, 55, 91, 64, 89]
# Important you are not allowed to use the max or min functions. The output words must match the example. i.e
# The highest score in the class is: x
studentScores = input("Input a list of student scores.\n")
studentScores = studentScores.split(" ")
highest = 0
for i in studentScores:
    if int(i) > highest:
        highest = int(i)

print(f'The highest score in the class is: {highest}')

# * Exercise 3 - Adding Even Numbers
# You are going to write a program that calculates the sum of all the even numbers from 1 to X. If X is 100 then the first even number would be 2 and the last one is 100:
# i.e. 2 + 4 + 6 + 8 +10 ... + 98 + 100
# Important, there should only be 1 print statement in your console output. It should just print the final total and not every step of the calculation.
# Also, we will constrain the inputs to only take numbers from 0 to a max of 1000. 

number = int(input("Enter an number between 0 and 1000: "))
listOfNumbers = []
result = 0
for i in range(2, number + 1, 2):
    result += i
print(result)

# * Exercise 4 - Fizzbuzz
# You are going to write a program that automatically prints the solution to the FizzBuzz game. These are the rules of the FizzBuzz game:
#     - Your program should print each number from 1 to 100 in turn and include number 100.
#     - When the number is divisible by 3 then instead of printing the number it should print "Fizz".
#     - When the number is divisible by 5, then instead of printing the number it should print "Buzz".`
#     - And if the number is divisible by both 3 and 5 e.g. 15 then instead of the number it should print "FizzBuzz"
# e.g. it might start off like this:
# 1
# 2
# Fizz
# 4
# Buzz
# Fizz
# 7
# 8
# Fizz
# Buzz
# 11
# Fizz
# 13
# 14
# FizzBuzz

for i in range(1,101):
    if i % 3 == 0 and i % 5 != 0:
        print("Fizz")
    elif i % 5 == 0 and i % 3 != 0:
        print("Buzz")
    elif i % 3 == 0 and i % 5 == 0:
        print("FizzBuzz")
    else:
        print(i)
