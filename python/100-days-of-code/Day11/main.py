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
wrongInputCounter = 0
playerTurn = True


def CounterIsExceeded(counter):
    wrongInputCounter = counter
    if wrongInputCounter == 3:
        print("More than 3 wrong inputs. Exiting the program. Bye.")
        exit()

def StartGame(counter):
    money = 1000
    wrongInputCounter = counter
    start = input("Welcome do you want to play some blackjack?\nType 'y' to play or 'n' to exit: ")
    if start == "y":
        wrongInputCounter = 0
        print(art.logo)
        money = Bet(money = money, counter = wrongInputCounter)
        BlackJack(money)
    elif start == "n":
        print("Bye!")
    else:
        wrongInputCounter += 1
        print("Wrong input. Try again.")
        CounterIsExceeded(wrongInputCounter)
        StartGame(wrongInputCounter)
        
def BlackJack(money):
    os.system('cls')
    print(art.logo)
    print(f'Remaining money: ${money}')
    initialDistribution = InitialHand()
    PrintScreen(player = initialDistribution[1], dealer = initialDistribution[2])
    
def PrintScreen(player, dealer):
    playerOutput = []
    dealerOutput = []
    for i in player:
        playerOutput.append(i)
    for j in dealer:
        dealerOutput.append(j)
    if playerTurn == True:
        print()
    print(playerOutput, dealerOutput)

def InitialHand():
    cards = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 10,
    "Q": 10,
    "K": 10,
    "A": 10
}
    playerHand = {}
    dealerHand = {}
    while len(playerHand) < 2:
        keyX = random.choice(list(cards.keys()))
        valueX = cards[keyX]
        playerHand[keyX] = valueX
        del cards[keyX]
        keyY = random.choice(list(cards.keys()))
        valueY = cards[keyY]
        dealerHand[keyY] = valueY
        del cards[keyY]
    return cards, playerHand, dealerHand


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
        return money - bet
    elif bet > money:
        print(f'You cannot bet that much. You do not have enough money.')
        wrongInputCounter += 1
        CounterIsExceeded(wrongInputCounter)
        return Bet(money = money, counter = wrongInputCounter)

StartGame(counter = wrongInputCounter)