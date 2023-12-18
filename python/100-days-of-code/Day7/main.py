import random, hangman_art, hangman_words
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

def ReplaceUnderscore(randomWord, underscores, guess, lives):
    letterCounter = 0
    for position in range(len(randomWord)):
        letter = randomWord[position]
        if letter == guess:
            letterCounter += 1
            underscores[position] = letter
    if letterCounter == 0:
            lives -= 1
            if lives > 0:
                print(f'That was a wrong guess.')
                print(f'Lives remaining: {lives}')
                PrintStage(lives)
            else:
                print(f'Game Over.')
                print(f'Correct word {randomWord}')
                exit()
    return underscores, lives

def GuessLetter(previousOnes):
    guess = input("Guess a letter: ")
    guess = guess.lower()
    check = guess.isnumeric()
    if check == True:
        print(f'Sorry your input cannot be a number. Please provide an letter.')
        guess = GuessLetter()
    if guess not in previousOnes:
        previousOnes += guess
    else:
        print(f'You already used this letter.') 
    return guess, previousOnes

def PrintStage(lives):
    print(hangman_art.stages[lives])

def Game():
    randomWord = random.choice(hangman_words.wordList)
    print(randomWord)
    result = GenerateUnderscores(randomWord)
    lives = 7
    previousOnes = ""
    while "_" in result:
        guess = GuessLetter(previousOnes)
        previousOnes = guess[1]
        print(f'Letters which you already used: {previousOnes.upper()}')
        underscores = ReplaceUnderscore(randomWord, result, guess[0], lives)
        lives = underscores[1]
        print(f"{' '.join(underscores[0])}")
    print("You beat the game! :)")

print(hangman_art.logo)
Game()



    

