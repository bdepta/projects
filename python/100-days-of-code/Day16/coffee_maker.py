class CoffeeMaker:
    def __init__(self):
        self.resources = {
            "water": 300,
            "milk": 200,
            "coffee": 100
        }
    
    def report(self):
        print(f"Water: {self.resources['water']}ml\nMilk: {self.resources['milk']}ml\nCoffee: {self.resources['coffee']}g")
    
    def are_resources_sufficient(self, drink):
        for i in self.resources:
            if drink[i] > self.resources[i]:
                print(f"Sorry there is not enough {i}. Please try another drink or consider refilling resources.")
                return False                
                if self.resources[i] == 0:
                    print(f"We have no {i}, please refill you coffee machine.")
                    return False
        return True
    
    def make_coffee(self, drink):
        for i in self.resources:
            self.resources[i] = self.resources[i] - drink.ingredients[i]
        print(f"Here is your {drink.name} ☕️. Enjoy!")
                