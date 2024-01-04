# Make your own "Choose Your Own Adventure" game. Use conditionals such as if, else, and elif statements to lay out the logic and the story's path in your program.
print('''
*******************************************************************************
          |                   |                  |                     |
 _________|________________.=""_;=.______________|_____________________|_______
|                   |  ,-"_,=""     `"=.|                  |
|___________________|__"=._o`"-._        `"=.______________|___________________
          |                `"=._o`"=._      _`"=._                     |
 _________|_____________________:=._o "=._."_.-="'"=.__________________|_______
|                   |    __.--" , ; `"=._o." ,-"""-._ ".   |
|___________________|_._"  ,. .` ` `` ,  `"-._"-._   ". '__|___________________
          |           |o`"=._` , "` `; .". ,  "-._"-._; ;              |
 _________|___________| ;`-.o`"=._; ." ` '`."\` . "-._ /_______________|_______
|                   | |o;    `"-.o`"=._``  '` " ,__.--o;   |
|___________________|_| ;     (#) `-.o `"=.`_.--"_o.-; ;___|___________________
____/______/______/___|o;._    "      `".o|o_.--"    ;o;____/______/______/____
/______/______/______/_"=._o--._        ; | ;        ; ;/______/______/______/_
____/______/______/______/__"=._o--._   ;o|o;     _._;o;____/______/______/____
/______/______/______/______/____"=._o._; | ;_.--"o.--"_/______/______/______/_
____/______/______/______/______/_____"=.o|o_.--""___/______/______/______/____
/______/______/______/______/______/______/______/______/______/______/_____ /
*******************************************************************************
''')
print("Welcome to Treasure Island.\nYour mission is to find the treasure.")



def game ():
    direction = input('You are at a crossroad. Where do you want to go? Type "left" or "right".\n')
    direction = direction.lower()
    if direction == "left":
        print(f'Excellent {direction} was a good decision.\n Now you come to the lake.There is an island in the middle of the lake.')
        action = input('There is an island in the middle of the lake. Type "wait" to wait for a boat. Type "swim" to swim across.\n')
        action = action.lower()
        if action == "wait":
            print(f'Nice one! Decision to {action} was a good one. You arrive at the island unharmed. There is a house with 3 doors.')
            color = input('One red, one yellow and one blue. Which color do you choose?\n')
            color = color.lower()
            if color == "red":
                print(f'You chosen {color} one. You have been burned by fire.')
                tryAgain = input("Do you want to try again? Type 'yes' to start from beginning or any character else to exit.\n")
                retry(tryAgain)
            elif color == "blue":
                print(f'You chosen {color} one. You have been eaten by beasts.')
                tryAgain = input("Do you want to try again? Type 'yes' to start from beginning or any character else to exit.\n")
                retry(tryAgain)
            elif color == "yellow":
                print(f'You chosen {color} one.')
                print('''
                                    ,.        ,.      ,.
                                    ||        ||      ||  ()
     ,--. ,-. ,.,-.  ,--.,.,-. ,-.  ||-.,.  ,.|| ,-.  ||-.,. ,-. ,.,-.  ,--.
    //`-'//-\\||/|| //-||||/`'//-\\ ||-'||  ||||//-\\ ||-'||//-\\||/|| ((`-'
    ||   || |||| ||||  ||||   || || ||  || /|||||| || ||  |||| |||| ||  ``.
    \\,-.\\-//|| || \\-||||   \\-|| ||  ||//||||\\-|| ||  ||\\-//|| || ,-.))
     `--' `-' `' `'  `-,|`'    `-^-``'  `-' `'`' `-^-``'  `' `-' `' `' `--'
                      //           .--------.
                  ,-.//          .: : :  :___`.
                  `--'         .'!!:::::  \\_\ `.
                          : . /%O!!::::::::\\_\. \
                         [""]/%%O!!:::::::::  : . \
                         |  |%%OO!!::::::::::: : . |
                         |  |%%OO!!:::::::::::::  :|
                         |  |%%OO!!!::::::::::::: :|
                :       .'--`.%%OO!!!:::::::::::: :|
              : .:     /`.__.'\%%OO!!!::::::::::::/
             :    .   /        \%OO!!!!::::::::::/
            ,-'``'-. ;          ;%%OO!!!!!!:::::'
            |`-..-'| |   ,--.   |`%%%OO!!!!!!:'
            | .   :| |_.','`.`._|  `%%%OO!%%'
            | . :  | |--'    `--|    `%%%%'
            |`-..-'| ||   | | | |     /__\`-.
            \::::::/ ||)|/|)|)|\|           /
    ---------`::::'--|._ ~**~ _.|----------( -----------------------
               )(    |  `-..-'  |           \    ______
               )(    |          |,--.       ____/ /  /\\ ,-._.-'
            ,-')('-. |          |\`;/   .-()___  :  |`.!,-'`'/`-._
           (  '  `  )`-._    _.-'|;,|    `-,    \_\__\`,-'>-.,-._
            `-....-'     ````    `--'      `-._       (`- `-._`-.   

                      You have won the game!

                      ''')
            else:
                print("It wasn't a good pick. You lost. Please try again.")
                tryAgain = input("Do you want to try again? Type 'yes' to start from beginning or any character else to exit.\n")
                retry(tryAgain)
        else:
            print(f'Oh no! You were attacked by a shark. Game over. Please try again.')
            tryAgain = input("Do you want to try again? Type 'yes' to start from beginning or any character else to exit.\n")
            retry(tryAgain)
    else:
        print(f"That's bad! Choosing {direction} wasn't a good decision. You fall into a hole. Please try again.")
        tryAgain = input("Do you want to try again? Type 'yes' to start from beginning or any character else to exit.\n")
        retry(tryAgain)

def retry(status):
    status = status.lower()
    if status == "yes":
        game()
    else:
        print('Maybe next time you will get this. Bye!')
        exit()

game()