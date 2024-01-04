
# * Exercise 1 - Grading Program
# You have access to a database of student_scores in the format of a dictionary. The keys in student_scores are the names of the students and the values are their exam scores.
# Write a program that converts their scores to grades. By the end of your program, you should have a new dictionary called student_grades that should contain student names for keys and their grades for values.
# The final version of the student_grades dictionary will be checked.
# DO NOT modify lines 1-7 to change the existing student_scores dictionary.
# DO NOT write any print statements.
# This is the scoring criteria:
# Scores 91 - 100: Grade = "Outstanding"
# Scores 81 - 90: Grade = "Exceeds Expectations"
# Scores 71 - 80: Grade = "Acceptable"
# Scores 70 or lower: Grade = "Fail"
studentScores = {
  "Harry": 81,
  "Ron": 78,
  "Hermione": 99, 
  "Draco": 74,
  "Neville": 62,
}

studentGrades = {}

for key in studentScores:
    if studentScores[key] > 90:
        studentGrades[key] = "Outstanding"
    elif studentScores[key] > 80:
        studentGrades[key] = "Exceeds Expectations"
    elif studentScores[key] > 70:
        studentGrades[key] = "Acceptable"
    else:
        studentGrades[key] = "Fail"

print(studentGrades)

# * Exercise 2 - Dictionary in List
# You are going to write a program that adds to a travel_log. You can see a travel_log which is a List that contains 2 Dictionaries. Your job is to create a function that can add new countries to this list.
# Write a function that will work with the following line of code on line 21 to add the entry for Brazil to the travel_log.
# add_new_country("Brazil", 5, ["Sao Paulo", "Rio de Janeiro"])
# DO NOT modify the travel_log directly. The goal is to create a function that modifies it.

country = input() # Add country name
visits = int(input()) # Number of visits
listOfCities = eval(input()) # create list from formatted string

travelLog = [
  {
    "country": "France",
    "visits": 12,
    "cities": ["Paris", "Lille", "Dijon"]
  },
  {
    "country": "Germany",
    "visits": 5,
    "cities": ["Berlin", "Hamburg", "Stuttgart"]
  },
]

def AddNewCountry(country, visits, listOfCities):
    length = len(travelLog)
    travelLog.append({})
    travelLog[length]["country"] = country
    travelLog[length]["visits"] = visits
    travelLog[length]["cities"] = listOfCities
# Do not change the code below 👇
AddNewCountry(country, visits, listOfCities)
print(f"I've been to {travelLog[2]['country']} {travelLog[2]['visits']} times.")
print(f"My favourite city was {travelLog[2]['cities'][0]}.")