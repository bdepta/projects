from menu import Menu, MenuItem
from coffee_maker import CoffeeMaker
from money_machine import MoneyMachine

menu = Menu()
coffee_maker = CoffeeMaker()
money_machine = MoneyMachine()
counter = 0
while True:
    customer_order = str(input(f"What would you like? ({menu.get_items()}): ")).lower()
    if customer_order == "espresso" or customer_order == "latte" or customer_order == "cappuccino":
        product_details = menu.find_drink(customer_order)
        if coffee_maker.are_resources_sufficient(product_details.ingredients) == True:
            if money_machine.make_payment(product_details.cost) == True:
                money_machine.money += product_details.cost
                coffee_maker.make_coffee(product_details)
            else:
                print("Please start from beginning.")
    elif customer_order == "report":
        coffee_maker.report()
        money_machine.report()
    elif customer_order == "off":
        exit()
    elif customer_order == "refill":
        coffee_maker = CoffeeMaker()
    else:
        counter += 1
        print("There is no such action. Please try again.")
        if counter > 3:
            print("There were more than 3 wrong inputs.")
            exit()
    
    
    
