############### Blackjack Project #####################

#Difficulty Normal 😎: Use all Hints below to complete the project.
#Difficulty Hard 🤔: Use only Hints 1, 2, 3 to complete the project.
#Difficulty Extra Hard 😭: Only use Hints 1 & 2 to complete the project.
#Difficulty Expert 🤯: Only use Hint 1 to complete the project.

############### Our Blackjack House Rules #####################

## The deck is unlimited in size. 
## There are no jokers. 
## The Jack/Queen/King all count as 10.
## The the Ace can count as 11 or 1.
## Use the following list as the deck of cards:
## cards = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
## The cards in the list have equal probability of being drawn.
## Cards are not removed from the deck as they are drawn.
## The computer is the dealer.
## If Dealer have less than 17 points it has to pick another card.
import art, os, random

def CounterIsExceeded(counter):
    wrongInputCounter = counter
    if wrongInputCounter == 3:
        print("More than 3 wrong inputs. Exiting the program. Bye.")
        exit()

def ResetCounter():
    counter = 0
    return counter

def StartGame(counter):
    os.system('cls')
    money = 1000
    wrongInputCounter = counter
    start = input("Welcome do you want to play some blackjack?\nType 'yes' to play or 'no' to exit: ")
    if start == "yes":
        os.system('cls')
        wrongInputCounter = ResetCounter()
        print(art.logo)
        money = Bet(money = money, counter = wrongInputCounter)
        distribution = InitialHand()
        BlackJack(money[0], money[1] ,distribution, playerTurn=True)
    elif start == "no":
        print("Bye!")
    else:
        wrongInputCounter += 1
        print("Wrong input. Try again.")
        CounterIsExceeded(wrongInputCounter)
        StartGame(wrongInputCounter)
        
def RestartGame(money, restart):
    wrongInputCounter = restart
    restartOption = input("Do you want to play another round? Type 'yes' to play again or type 'no' to exit the game: ").lower()
    if restartOption == "no":
        print(f'You end the game with: $ {money}. Bye!')
        exit()
    elif restartOption == "yes":
        os.system('cls')
        wrongInputCounter = ResetCounter()
        print(art.logo)
        newMoney = Bet(money = money, counter = wrongInputCounter)
        distribution = InitialHand()
        BlackJack(newMoney[0], newMoney[1] ,distribution, playerTurn=True)
    else:
        wrongInputCounter += 1
        print("Wrong input. Try again.")
        CounterIsExceeded(wrongInputCounter)
        StartGame(wrongInputCounter)

def InitialHand():
    cards = {
    "2♣": 2,
    "2♦": 2,
    "2♥": 2,
    "2♠": 2,
    "3♣": 3,
    "3♦": 3,
    "3♥": 3,
    "3♠": 3,
    "4♣": 4,
    "4♦": 4,
    "4♥": 4,
    "4♠": 4,
    "5♣": 5,
    "5♦": 5,
    "5♥": 5,
    "5♠": 5,
    "6♣": 6,
    "6♦": 6,
    "6♥": 6,
    "6♠": 6,
    "7♣": 7,
    "7♦": 7,
    "7♥": 7,
    "7♠": 7,
    "8♣": 8,
    "8♦": 8,
    "8♥": 8,
    "8♠": 8,
    "9♣": 9,
    "9♦": 9,
    "9♥": 9,
    "9♠": 9,
    "10♣": 10,
    "10♦": 10,
    "10♥": 10,
    "10♠": 10,
    "J♣": 10,
    "J♦": 10,
    "J♥": 10,
    "J♠": 10,
    "Q♣": 10,
    "Q♦": 10,
    "Q♥": 10,
    "Q♠": 10,
    "K♣": 10,
    "K♦": 10,
    "K♥": 10,
    "K♠": 10,
    "A♣": 11,
    "A♦": 11,
    "A♥": 11,
    "A♠": 11

}
    playerHand = {}
    dealerHand = {}
    while len(playerHand) < 2:
        keyX = random.choice(list(cards.keys()))
        valueX = cards[keyX]
        playerHand[keyX] = valueX
        del cards[keyX]
        while len(dealerHand) < 1:
            keyY = random.choice(list(cards.keys()))
            valueY = cards[keyY]
            dealerHand[keyY] = valueY
            del cards[keyY]
    return cards, playerHand, dealerHand

def DefineScore(distribution):
    playerScore = 0
    dealerScore = 0
    for i in list(distribution[1].values()):
        playerScore += i
        if ("A♣" in distribution[1] or "A♦" in distribution[1] or "A♥" in distribution[1] or "A♠" in distribution[1]) and playerScore >= 21:
            distribution[1].remove(11)
            distribution[1].append(1)
    for j in list(distribution[2].values()):
        dealerScore += j
    playerHand = ", ".join(list(distribution[1]))
    dealerHand = ", ".join(list(distribution[2]))
    return playerScore, dealerScore, playerHand, dealerHand

def Bet(money, counter):
    wrongInputCounter = counter
    print(f'Remaining money: ${money}')
    try:
        bet = float(input("How much you would like to bet? $"))
    except:
        print(f'Your input must be float.')
        wrongInputCounter += 1
        CounterIsExceeded(wrongInputCounter)
        return Bet(money = money, counter = wrongInputCounter)
    if bet <= money:
        return (money - bet), bet
    elif bet > money:
        print(f'You cannot bet that much. You do not have enough money.')
        wrongInputCounter += 1
        CounterIsExceeded(wrongInputCounter)
        return Bet(money = money, counter = wrongInputCounter)

def PickCard(distribution, playerTurn):
    cards = distribution[0]
    playerHand = distribution [1]
    dealerHand = distribution[2]
    if playerTurn == True:
        keyX = random.choice(list(cards.keys()))
        valueX = cards[keyX]
        playerHand[keyX] = valueX
        del cards[keyX]
    elif playerTurn == False:
        keyY = random.choice(list(cards.keys()))
        valueY = cards[keyY]
        dealerHand[keyY] = valueY
        del cards[keyY]
    return cards, playerHand, dealerHand

def ChooseAction(counter, distribution, playerTurn, money,bet):
    wrongInputCounter = counter
    currentDistribution = distribution
    action = input("What's your next action? Type 'y' to get another card, type 'd' to double your bet and get another card or type 'p' to pass: ")
    score = DefineScore(currentDistribution)
    playerScore = score[0]
    dealerScore = score[1]
    if action == "p":
        playerTurn = False
        while dealerScore < 18:
            distribution = PickCard(currentDistribution, playerTurn)
            score = DefineScore(currentDistribution)
            dealerScore = score[1]
        BlackJack(money,bet, distribution, playerTurn)
    elif action == "y":
        distribution = PickCard(currentDistribution, playerTurn)
        BlackJack(money,bet, distribution, playerTurn)
    elif action == "d":
        #DoubleBet()
        distribution = PickCard(currentDistribution, playerTurn)
        money = money - bet
        bet = 2 * bet
        BlackJack(money, bet, distribution, playerTurn)
    else:
        wrongInputCounter += 1
        print("Wrong input. Try again.")
        CounterIsExceeded(wrongInputCounter)
        ChooseAction(counter = wrongInputCounter)

def BlackJack(money,bet,distribution, playerTurn):
    os.system('cls')
    print(art.logo)
    print(f'Remaining money: ${money}\n')
    score = DefineScore(distribution)
    print(f'Your cards: [{score[2]}], current score: {score[0]}\n')
    if playerTurn == True:
        print(f"Dealer's first card: {score[3]}, current score: {score[1]}\n")
    elif playerTurn == False:
        print(f"Dealer's cards: [{score[3]}], current score: {score[1]}\n")
    if playerTurn == True and score[0] < 21:
        wrongInputCounter = ResetCounter()  
        ChooseAction(counter = wrongInputCounter, distribution = distribution, playerTurn = playerTurn, money = money, bet =bet)
    elif (playerTurn == False and score[1] > 21) or (playerTurn == False and score[0] < 21 and score[0] > score[1]):
        print(f'You win 🙂.')
        wrongInputCounter = ResetCounter()  
        money = money + (bet+(2*bet))
        RestartGame(money,wrongInputCounter)
    elif (playerTurn == False and score[0] == score[1]):
        wrongInputCounter = ResetCounter()  
        print(f"It's a draw.")
        money = money + bet
        RestartGame(money,wrongInputCounter)
    else:
        wrongInputCounter = ResetCounter()  
        print(f'You lose 😒.')
        RestartGame(money,wrongInputCounter)


StartGame(counter = 0)