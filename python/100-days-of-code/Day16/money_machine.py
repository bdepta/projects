class MoneyMachine():
    def __init__(self):
        self.money = 0
    
    def report(self):
        print(f"Money: ${self.money}")

    def make_payment(self, cost):
        money_value = {
            "quarters": 0.25,
            "dimes": 0.10,
            "nickles": 0.05,
            "pennies": 0.01
        }
        inserted_money = {}
        money = 0
        counter = 0
        for i in money_value:
            try:
                inserted_money[i] = int(input(f"How many {i}?: "))
                continue
            except:
                counter += 1
                print("There is no such action. Please try again.")
                if counter > 3:
                    print("There were more than 3 wrong inputs.")
                    exit()       
        for i in inserted_money:
            money += inserted_money[i] * money_value[i]
            money = round(money, 2)
        if money < cost:
            print("Sorry that's not enough. Money refunded.")
            return False
        if money > cost:
            change = money - cost
            change = round(change, 2)
            print(f"Here is your ${change} dollars in change.")
            return True
        if money == cost:
            return True