#If the bill was $150.00, split between 5 people, with 12% tip. 
#Each person should pay (150.00 / 5) * 1.12 = 33.6
#Format the result to 2 decimal places = 33.60
#Tip: There are 2 ways to round a number. You might have to do some Googling to solve this.💪
#Write your code below this line 👇

def TotalBill( ):
    bill = float(input("What was the total bill? $"))
    bill = round(bill, 3)
    return bill

def TipPercentage( ):
    tip = int(input("How much tip would you like to give? Possible options: 10, 12 or 15.\n"))
    if tip == 10 or tip == 12 or tip == 15:
        return tip / 100
    else:
        print("Please choose correct option for the tip percentage. Possible options: 10, 12 or 15.")
        TipPercentage()
    
def NumberOfPeople( ):
    people = int(input("How many people to split the bill?\n"))
    if people < 0 or people == 0:
        print("You provided wrong number of people. Value cannot be null or negative.")
        NumberOfPeople()
    else:
        return people

print("Welcome to the tip calculator! 😊")
totalBill = 0
tipPercentage = 0
numberOfPeople = 0
totalBill = TotalBill()
tipPercentage = TipPercentage()
numberOfPeople = NumberOfPeople()

result = (totalBill + (totalBill * float(tipPercentage))) / numberOfPeople
result = round(result, 2)
result = "{:.2f}".format(result)
print(f'Each person should pay: ${result}')

