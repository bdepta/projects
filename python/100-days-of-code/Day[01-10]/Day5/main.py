#Password Generator Project
#e.g. 4 letter, 2 symbol, 2 number = g^2jk8&P
import random
def WelcomeScreen():
    try:
        nr_letters= int(input("How many letters would you like in your password?\n"))
        nr_numbers = int(input(f"How many numbers would you like?\n"))
        nr_symbols = int(input(f"How many symbols would you like?\n"))
    except:
        print(f'Your input must be integer.')
        exit()

    return nr_letters, nr_numbers, nr_symbols

def PasswordGenerator(nr_letters, nr_numbers, nr_symbols):
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+'] 
    password = ""
    l , n , s = 0 , 0 , 0
    while l < nr_letters:
        password += random.choice(letters)
        l += 1
    while n < nr_numbers:
        password += random.choice(numbers)
        n += 1
    while s < nr_symbols:
        password += random.choice(symbols)
        s += 1
    password = ''.join(random.sample(password,len(password)))
    print(f'Here is your password: {password}')




print("Welcome to the PyPassword Generator!") 
userInput = WelcomeScreen()
PasswordGenerator(userInput[0], userInput[1], userInput[2])

