
# * Blind Auction Start 
# The objective is to write a program that will collect the names and bids of different people. The program should ask for each bidder's name and their bid individually.
# Welcome to the secret auction program. 
# What is your name?: Angela
# What's your bid?: $123
# Are there any other bidders? Type 'yes' or 'no'.
# yes
# If there are other bidders, the screen should clear, so you can pass your phone to the next person. If there are no more bidders, then the program should display the name of the winner and their winning bid.
# The winner is Elon with a bid of $55000000000
# Use your knowledge of Python dictionaries and loops to solve this challenge.
import logo, os

def OtherBidders():
    os.system('cls')
    check = input("Are there any other bidders? Type 'yes' or 'no'.\n").lower()
    if check == "yes":
        os.system('cls')
        NewBidder()
    elif check == "no":
        os.system('cls')
        print(logo.logo + "\n\n\n\n\n\n")
        Winner()
    else:
        os.system('cls')
        print("Wrong input. Please provide correct one.")
        OtherBidders()

def NewBidder():
    newBidder = {}
    print(logo.logo + "\n")
    name = input("What is your name?: ")
    bid = int(input("What's your bid?: $"))
    newBidder["name"] = name
    newBidder["bid"] = bid
    bidders.append(newBidder)
    OtherBidders()
    
def Winner():
    winnerName = bidders[0]["name"]
    winnerBid = bidders[0]["bid"]
    for i in bidders:
        if i["bid"] > winnerBid:
            winnerName = i["name"]
            winnerBid = i["bid"]
    print(f'The winner is {winnerName} with a bid of ${winnerBid}!!')

def Restart():
    newAuction = input("Do you want to start an new auction? Type 'yes' or 'no'.\n").lower()
    if newAuction == "yes":
        NewBidder()
    elif newAuction == "no":
        exit()
    else:
        print("Wrong input. Please try correct one.")

bidders = []
NewBidder()