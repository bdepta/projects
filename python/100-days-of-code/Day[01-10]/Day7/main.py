import random, os, hangman_art, hangman_words
#* Step 1 
#* 1 - Randomly choose a word from the word_list and assign it to a variable called chosen_word.
#* 2 - Ask the user to guess a letter and assign their answer to a variable called guess. Make guess lowercase.
#* 3 - Check if the letter the user guessed (guess) is one of the letters in the chosen_word.
#* Step 2
#* 1: - Create an empty List called display.
    #For each letter in the chosen_word, add a "_" to 'display'.
    #So if the chosen_word was "apple", display should be ["_", "_", "_", "_", "_"] with 5 "_" representing each letter to guess.
#* 2: - Loop through each position in the chosen_word;
    #If the letter at that position matches 'guess' then reveal that letter in the display at that position.
    #e.g. If the user guessed "p" and the chosen word was "apple", then display should be ["_", "p", "p", "_", "_"]
#* 3: - Print 'display' and you should see the guessed letter in the correct position and every other letter replace with "_".
    #Hint - Don't worry about getting the user to guess the next letter. We'll tackle that in step 3.
#* Step 3
#* 1: - Use a while loop to let the user guess again. The loop should only stop once the user has guessed all the letters in the chosen_word and 'display' has no more blanks ("_"). Then you can tell the user they've won.
#* Step 4
#* 1: - Create a variable called 'lives' to keep track of the number of lives left. 
    #Set 'lives' to equal 6.
#* 2: - If guess is not a letter in the chosen_word,
    #Then reduce 'lives' by 1. 
    #If lives goes down to 0 then the game should stop and it should print "You lose."
#* 3: - print the ASCII art from 'stages' that corresponds to the current number of 'lives' the user has remaining.
#TODO Step 5
#* 1: - Update the word list to use the 'word_list' from hangman_words.py
#* 2: - Import the stages from hangman_art.py and make this error go away.
#* 3: - Import the logo from hangman_art.py and print it at the start of the game.
#TODO 4: - If the user has entered a letter they've already guessed, print the letter and let them know.
#TODO 5: - If the letter is not in the chosen_word, print out the letter and let them know it's not in the word.
def GenerateUnderscores(randomWord):
    k = len(randomWord)
    underscoresList = ["_"] * k
    return underscoresList

def ReplaceUnderscore(randomWord, underscores, guess, lives, previousOnes):       
    letterCounter = 0
    for position in range(len(randomWord)):
        letter = randomWord[position]
        if letter == guess:
            letterCounter += 1
            underscores[position] = letter
    if letterCounter == 0:
            lives -= 1
            print(f'\nThat was a wrong guess! :(')
            previousOnes += guess
    else:
        print(f'\nThat was a good guess! :)')
    return underscores, lives, previousOnes

def GuessLetter(result, previousOnes):
    guess = input("Guess a letter: ")
    guess = guess.lower()
    checkNumeric = guess.isnumeric()
    checkLength = len(guess)
    if checkNumeric != True and checkLength == 1:
        if guess in result or guess in previousOnes:
            print(f'You already used this letter. Provide different one.')
            guess = GuessLetter(result, previousOnes)
    else:
        print(f'\nSorry your input cannot be a null, number or string containing more than one letter. Please provide an letter.\n')
        guess = GuessLetter(result, previousOnes)
    return guess

def PrintStage(lives):
    print(hangman_art.stages[lives])

def RestartGame():
    restartOption = input("\nDo you want to start again? Please type 'yes' to restart or 'no' to exit the game. \n")
    restartOption = restartOption.lower()
    if restartOption == "yes":
        Game()
    elif restartOption == "no":
        exit()
    else:
        print("Wrong input! Bye.")
        exit()

def Game():
    os.system('cls')
    print(hangman_art.logo + "\n")
    language = input(f'Do you want to generate word in Polish or English?\n')
    if language.lower() == "english":
        randomWord = random.choice(hangman_words.wordListEnglish)
    elif language.lower() == "polish":
        randomWord = random.choice(hangman_words.wordListPolish)
    else:
        print("Wrong input!")
        RestartGame()
    randomWord = randomWord.lower()
    result = GenerateUnderscores(randomWord.lower())
    lives = 7
    previousOnes = ""
    PrintStage(lives)
    print(f'Lives remaining: {lives}\n')
    print(f"{' '.join(result)}\n")
    print(f'Letters which you already used: {previousOnes.upper()}\n')
    while "_" in result:
        guess = GuessLetter(result, previousOnes)
        underscores = ReplaceUnderscore(randomWord, result, guess[0], lives, previousOnes)
        result = underscores[0]
        lives = underscores[1]
        previousOnes = underscores[2]
        if lives <= 7 and lives > 0:
            os.system('cls')
            print(hangman_art.logo)
            PrintStage(lives)
            print(f'Lives remaining: {lives}\n')
            print(f"{' '.join(result)}\n")
        else:
            print(f'\nCorrect word was {randomWord.lower()}\n')
            print(f'Game Over.')
            RestartGame()
        print(f'Letters which you already used: {previousOnes.upper()}\n')
    print("You beat the game! :)")
    RestartGame()


Game()



    

