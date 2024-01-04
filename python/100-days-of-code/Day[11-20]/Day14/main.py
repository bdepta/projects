import random, os, art, game_data

asciiLogo = art.logo
asciiVs = art.vs

def CounterIsExceeded(counter):
    wrongInputCounter = counter
    if wrongInputCounter == 3:
        print("More than 3 wrong inputs. Exiting the program. Bye.")
        exit()

def ResetCounter():
    counter = 0
    return counter

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

def ChooseElement(data):
    x = random.choice(data)
    index = data.index(x)
    del data[index]
    return x, data

def CheckAnswer(answer, choiceA, choiceB, score):
    if answer == "a" and choiceA[0]['follower_count'] > choiceB[0]['follower_count']:
        score += 1
        choiceA = choiceB
        os.system('cls')
        print(asciiLogo)
        if score > 0: 
            print(f"That's correct! Current score: {score}\n")
    if answer == "a" and choiceA[0]['follower_count'] < choiceB[0]['follower_count']:
        print(f"That's not correct! Final score: {score}")
        exit()
    if answer == "b" and choiceA[0]['follower_count'] > choiceB[0]['follower_count']:
        print(f"That's not correct! Final score: {score}")
        exit()
    if answer == "b" and choiceA[0]['follower_count'] < choiceB[0]['follower_count']:
        print("That's correct!\n")
        score += 1
        choiceA = choiceB
        os.system('cls')
        print(asciiLogo)
        if score > 0: 
            print(f"That's correct! Current score: {score}\n")
    return score, choiceA

def StartGame():
    gameData = game_data.data
    score = 0
    os.system('cls')
    print(asciiLogo)
    choiceA = ChooseElement(data = gameData)
    gameData = choiceA[1]
    while len(gameData) >= 1:
        counter = ResetCounter()
        correctInput = True    
        choiceB = ChooseElement(data = gameData)
        gameData = choiceB[1]
        print(f"Compare A: {choiceA[0]['name']}, {choiceA[0]['description']}, {choiceA[0]['country']}\n {asciiVs}\nCompare B: {choiceB[0]['name']}, {choiceB[0]['description']}, {choiceB[0]['country']}")
        while correctInput == True:
            answer = str(input("Who has more followers? Type 'A' or 'B': ")).lower()
            if answer == "a" or answer == "b":
                checkAnswer = CheckAnswer(answer = answer, choiceA = choiceA, choiceB = choiceB, score = score)
                score = checkAnswer[0]
                choiceA = checkAnswer[1]
                correctInput = False
            else:
                counter += 1
                CounterIsExceeded(counter)
    print(f"You win the game, there is no more option to choose from. Congratulations.")
    exit() 



StartGame()