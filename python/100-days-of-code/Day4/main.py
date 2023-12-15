import random
def PrintAscii(choice):
    if choice == "rock":
        print('''
    _______
---'   ____)
      (_____)
      (_____)
      (____)
---.__(___)
''')
    elif choice == "paper":
        print('''
    _______
---'   ____)____
          ______)
          _______)
         _______)
---.__________)
''')
    elif choice == "scissors":
        print('''
    _______
---'   ____)____
          ______)
       __________)
      (____)
---.__(___)
''')
        
def Restart():
    choice = input("Do you want to try again? Type 'Yes' to try again or 'No' to exit the game.\n")
    choice = choice.lower()
    if choice == "yes":
        StartGame()
    elif choice == "no":
        exit()
    else:
        print("Wrong option again. Closing the program.")
        exit()

def WrongChoice():
    print("Looks like you've made an wrong choice.")
    Restart()

def StartGame():
    optionList = ['rock','paper','scissors']
    computerOption = random.choice(optionList)
    try:
        humanInput = int(input("What do you choose? Type 0 for Rock, 1 for Paper or 2 for Scissors.\n"))
    except:
        WrongChoice()
    if humanInput >= 3:
        WrongChoice()
    humanOption = optionList[humanInput]
    print(f'You chose:')
    humanOptionOutput = PrintAscii(humanOption)
    print(f'Computer Chose:')
    computerOptionOutput = PrintAscii(computerOption)
    Game(computerOption, humanOption)

def Game(computerOption, humanOption):
    # Draw 
    if (computerOption == "rock" and humanOption == "rock") or (computerOption == "paper" and humanOption == "paper") or (computerOption == "scissors" and humanOption == "scissors"):
        print(f"It's a draw!")
        Restart()
    # Computer Wins
    if (computerOption == "rock" and humanOption == "scissors") or (computerOption == "paper" and humanOption == "rock") or (computerOption == "scissors" and humanOption == "paper"):
        print(f'You lose.')
        Restart()
    # Human Wins
    if (computerOption == "scissors" and humanOption == "rock") or (computerOption == "rock" and humanOption == "paper") or (computerOption == "paper" and humanOption == "scissors"):
        print(f'You win.')
        Restart()

print(f'Welcome in the RPS Game!')
StartGame()

