import Day10.art as art
# * Step 1:
# * 1: Create a function called 'encrypt' that takes the 'text' and 'shift' as inputs.
# * 2: Inside the 'encrypt' function, shift each letter of the 'text' forwards in the alphabet by the shift amount and print the encrypted text.  
    #e.g. 
    #plain_text = "hello"
    #shift = 5
    #cipher_text = "mjqqt"
    #print output: "The encoded text is mjqqt"

    ##HINT: How do you get the index of an item in a list:
    #https://stackoverflow.com/questions/176918/finding-the-index-of-an-item-in-a-list

    ##🐛Bug alert: What happens if you try to encode the word 'civilization'?🐛
# * 3: Call the encrypt function and pass in the user inputs. You should be able to test the code and encrypt a message. 
# * Step 2:
# * 1: Create a different function called 'decrypt' that takes the 'text' and 'shift' as inputs.
# * 2: Inside the 'decrypt' function, shift each letter of the 'text' *backwards* in the alphabet by the shift amount and print the decrypted text.  
  #e.g. 
  #cipher_text = "mjqqt"
  #shift = 5
  #plain_text = "hello"
  #print output: "The decoded text is hello"
# * 3: Check if the user wanted to encrypt or decrypt the message by checking the 'direction' variable. Then call the correct function based on that 'drection' variable. You should be able to test the code to encrypt *AND* decrypt a message.
# * Step 3:
# * 1: Combine the encrypt() and decrypt() functions into a single function called caesar().
# * 2: Call the caesar() function, passing over the 'text', 'shift' and 'direction' values.
# * Step 4:
# * 1: Import and print the logo from art.py when the program starts.
# * 2: What if the user enters a shift that is greater than the number of letters in the alphabet?
#Try running the program and entering a shift number of 45.
#Add some code so that the program continues to work even if the user enters a shift number greater than 26. 
#Hint: Think about how you can use the modulus (%).
# * 3: What happens if the user enters a number/symbol/space?
#Can you fix the code to keep the number/symbol/space when the text is encoded/decoded?
#e.g. start_text = "meet me at 3"
#end_text = "•••• •• •• 3"
# * 4: Can you figure out a way to ask the user if they want to restart the cipher program?
#e.g. Type 'yes' if you want to go again. Otherwise type 'no'.
#If they type 'yes' then ask them for the direction/text/shift again and call the caesar() function again?
#Hint: Try creating a while loop that continues to execute the program if the user types 'yes'.

def CaesarCipher():
    print(art.logo)
    direction = input("Type 'encode' to encrypt, type 'decode' to decrypt:\n").lower()
    text = input("Type your message:\n").lower()
    shift = int(input("Type the shift number:\n"))
    if direction == "encode":
        print(encrypt(text=text, shift=shift))
        RestartProgram()
    elif direction == "decode":
        print(decrypt(text=text, shift=shift))
        RestartProgram()

def RestartProgram():
    restartOption = input("\nDo you want to try again? Please type 'yes' to restart or 'no' to exit the program. \n")
    restartOption = restartOption.lower()
    if restartOption == "yes":
        CaesarCipher()
    elif restartOption == "no":
        exit()
    else:
        print("Wrong input! Bye.")
        exit()

def encrypt(text, shift):
    cipherList = []
    for i in text:
        if i not in alphabet:
            cipherList += i
        else:
            index = alphabet.index(i)
            cipherIndex = index + shift
            if cipherIndex < len(alphabet):
                cipherList += alphabet[cipherIndex]
            else:
                cipherIndex = cipherIndex - len(alphabet)
                cipherList += alphabet[cipherIndex]
    cipherText = "".join(cipherList)
    return cipherText

def decrypt(text, shift):
    decryptedList = []
    for i in text:
        index = alphabet.index(i)
        cipherIndex = index - shift
        if cipherIndex < 0:
            cipherIndex = cipherIndex + len(alphabet)
            decryptedList += alphabet[cipherIndex]
        else:
            decryptedList += alphabet[cipherIndex]
    decryptedText = "".join(decryptedList)
    return decryptedText


alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
CaesarCipher()



