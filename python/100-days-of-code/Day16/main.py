from menu import Menu, MenuItem
from coffee_maker import CoffeeMaker
#from money_machine import MoneyMachine

menu = Menu()
coffee_maker = CoffeeMaker()
while True:
    customer_order = str(input(f"What would you like? ({menu.get_items()}): "))
    if customer_order == "espresso" or customer_order == "latte" or customer_order == "cappuccino":
        product_details = menu.find_drink(customer_order)
        if coffee_maker.are_resources_sufficient(product_details.ingredients) == True:
            coffee_maker.make_coffee(product_details)
    elif customer_order == "report":
        coffee_maker.report()
    elif customer_order == "off":
        exit()
    elif customer_order == "refill":
        coffee_maker = CoffeeMaker()
    
    
    
