
# TODO: Number Guessing Game
# Objectives:
# Include an ASCII art logo.
# Allow the player to submit a guess for a number between 1 and 100.
# Check user's guess against actual answer. Print "Too high." or "Too low." depending on the user's answer. 
# If they got the answer correct, show the actual answer to the player.
# Track the number of turns remaining.
# If they run out of turns, provide feedback to the player. 
# Include two different difficulty levels (e.g., 10 guesses in easy mode, only 5 guesses in hard mode).
import random, os, art


def CounterIsExceeded(counter):
    wrongInputCounter = counter
    if wrongInputCounter == 3:
        print("More than 3 wrong inputs. Exiting the program. Bye.")
        exit()

def ResetCounter():
    counter = 0
    return counter

def GuessNumber(counter, number, lives):
    while lives > 0:
        print(f"You have {lives} attempts remaining to guess the number.")
        try:
            guess = int(input("Make a guess: "))
        except:
            counter += 1
            print("Wrong input. Try again.")
            CounterIsExceeded(counter)
            GuessNumber(counter, number, lives)
        if guess < 1 or guess > 100:
            counter += 1
            print("Wrong input. Try again.")
            CounterIsExceeded(counter)
            GuessNumber(counter, number, lives)
        if guess == number:
            print(f"You win. Congratulations. Correct number was: {number}")
            RestartGame(restart = 0)
        if guess < number:
            lives -= 1
            print("Too low.")
        if guess > number:
            lives -= 1
            print("Too high.")
    print(f"You've run out of guesses, you lose.\nCorrect number was: {number}")
    RestartGame(restart = 0)

def RestartGame(restart):
    restartOption = input("Do you want to play another round? Type 'yes' to play again or type 'no' to exit the game: ").lower()
    if restartOption == "no":
        print(f'Bye!')
        exit()
    elif restartOption == "yes":
        os.system('cls')
        StartGame(restart)
    else:
        wrongInputCounter += 1
        print("Wrong input. Try again.")
        CounterIsExceeded(wrongInputCounter)
        RestartGame(wrongInputCounter)

def StartGame(counter):
    os.system('cls')
    number = random.randint(1,100)
    print(art.logo)
    difficulty = input(f"Welcome to the Number Guessing Game!\nPlease choose the difficulty. Type 'easy' or 'hard': ")
    if difficulty == "easy":
        GuessNumber(counter = 0, number = number, lives = 10)
    elif difficulty == "hard":
        GuessNumber(counter = 0, number = number, lives = 5)
    else:
        counter += 1
        CounterIsExceeded(counter)
        StartGame(counter)




StartGame(counter = 0)
