import art, os
# TODO Calculator

def Add(x,y):
    return x + y
def Sub(x,y):
    return x - y
def Mul(x,y):
    return x * y
def Div(x,y):
    if y == 0:
        print('Dividend cannot be zero.')
        exit()
    else:
        return x / y
def Start():
    os.system('cls')
    print(art.logo)
    firstNumber = float(input("What's the first number?: "))
    Operation(x = firstNumber)
def Operation(x):
    for i in operations:
        print(i)
    operationSymbol = str(input("Pick an operation: "))
    secondNumber = float(input("What's the second number?: "))
    if operationSymbol in operations:
        calculationFunction = operations[operationSymbol]
        result = calculationFunction(x = x, y = secondNumber)
        print(f'{x} {operationSymbol} {secondNumber} = {result}')
        Resume(x = result)
    else:
        print("Wrong operation. Please try again.")
        exit()   
    
def Resume(x):
    firstNumber = x
    check = input(f'Type "c" to continue calculation with {firstNumber}, type "n" for new calculation or "exit" to exit the program:  ')
    if check == "c":
        Operation(x = firstNumber)
    elif check == "n":
        Start()
    elif check == "exit":
        exit()
    else:
        print("Wrong input. Please try again.")
        Resume(firstNumber)

operations = {
    "+": Add,
    "-": Sub,
    "*": Mul,
    "/": Div,
}

Start()


