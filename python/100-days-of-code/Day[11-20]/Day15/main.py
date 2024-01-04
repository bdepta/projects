import os
menu = {
    "espresso": {
        "ingredients": {
            "water": 50,
            "milk": 0,
            "coffee": 18,
        },
        "cost": 1.5,
    },
    "latte": {
        "ingredients": {
            "water": 200,
            "milk": 150,
            "coffee": 24,
        },
        "cost": 2.5,
    },
    "cappuccino": {
        "ingredients": {
            "water": 250,
            "milk": 100,
            "coffee": 24,
        },
        "cost": 3.0,
    }
}



def CounterIsExceeded(counter):
    wrongInputCounter = counter
    if wrongInputCounter == 3:
        print("More than 3 wrong inputs. Exiting the program. Bye.")
        exit()

def ResetCounter():
    counter = 0
    return counter

def Restart(restart):
    restartOption = input("Do you want to another coffee? Type 'yes' to make another one or type 'off' to turn off the coffee machine: ").lower()
    if restartOption == "off":
        print(f'Bye!')
        exit()
    elif restartOption == "yes":
        os.system('cls')
        Express(restart)
    else:
        wrongInputCounter += 1
        print("Wrong input. Try again.")
        CounterIsExceeded(wrongInputCounter)
        Restart(wrongInputCounter)

def ShowResources(resources, money):
    print(f"Water: {resources['water']}ml\nMilk: {resources['milk']}ml\nCoffee: {resources['coffee']}g\nMoney: ${money}")

def CheckResources(resources, ingredients):
    for i in resources:
        if ingredients[i] > resources[i]:
            print(f"Sorry there is not enough {i}. Please try another drink or consider refilling resources.")
            if resources[i] == 0:
                print(f"We have no {i}, please refill you coffee machine.")
            Express(resources)

def PayForCoffee(cost):
    moneyValue = {
        "quarters": 0.25,
        "dimes": 0.10,
        "nickles": 0.05,
        "pennies": 0.01
    }
    insertedMoney = {}
    money = 0
    counter = ResetCounter()
    for i in moneyValue:
        insertedMoney[i] = int(input(f"How many {i}?: "))
    for i in insertedMoney:
        money += insertedMoney[i] * moneyValue[i]
        money = round(money, 2)
    if money < cost:
        print("Sorry that's not enough. Money refunded.")
        counter += 1
        CounterIsExceeded(counter)
        PayForCoffee(cost=cost)
    if money > cost:
        change = money - cost
        change = round(change, 2)
        print(f"Here is your ${change} dollars in change.") 

def PrepareDrink(resources, drink):
    CheckResources(resources=resources, ingredients=drink["ingredients"])
    PayForCoffee(cost=drink["cost"])
    for i in resources:
        resources[i] = resources[i] - drink["ingredients"][i]
    return resources

def Express(resources):
    counter = ResetCounter()
    money = 0
    while True:
        choice = str(input("What would you like? (espresso/latte/cappuccino): ")).lower()
        if choice == "espresso":
            resources = PrepareDrink(resources, menu[choice])
            money += menu[choice]["cost"]
            print(f"Here is your {choice} ☕. Enjoy!")
        elif choice == "latte":
            resources = PrepareDrink(resources, menu[choice])
            money += menu[choice]["cost"]
            print(f"Here is your {choice} ☕. Enjoy!")
        elif choice == "cappuccino":
            resources = PrepareDrink(resources, menu[choice])
            money += menu[choice]["cost"]
            print(f"Here is your {choice} ☕. Enjoy!")
        elif choice == "report":
            ShowResources(resources, money)
        elif choice == "off":
            exit()
        elif choice == "refill":
            resources = {
                "water": 300,
                "milk": 200,
                "coffee": 100,
            }
            print(f"Machine resources were refilled.\nMoney were collected. Total amount of money was :{money}.")
            money = 0
        else:
            print(f"Your input was: '{choice}'. It's not allowed. Please check your input.")
            counter += 1
            CounterIsExceeded(counter)

resources = {
    "water": 300,
    "milk": 200,
    "coffee": 100,
}
Express(resources=resources)