#TODO: Create a letter using starting_letter.txt 
#for each name in invited_names.txt
#Replace the [name] placeholder with the actual name.
#Save the letters in the folder "ReadyToSend".




with open("./Input/Letters/starting_letter.txt") as file:
    letter = file.read()
with open("./Input/Names/invited_names.txt") as file:
    names = file.read()
names_list = names.split('\n')

for i in names_list:
    personal_letter = letter
    personal_letter = personal_letter.replace("[name]", i)
    with open(f"./Output/ReadyToSend/LetterTo{i}", mode="w") as file:
        file.write(personal_letter) 

#Hint1: This method will help you: https://www.w3schools.com/python/ref_file_readlines.asp
    #Hint2: This method will also help you: https://www.w3schools.com/python/ref_string_replace.asp
        #Hint3: THis method will help you: https://www.w3schools.com/python/ref_string_strip.asp