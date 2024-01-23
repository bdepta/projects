import pandas
#* 1. Create a dictionary in this format:
{"A": "Alfa", "B": "Bravo"}
file = "./nato_phonetic_alphabet.csv"
df = pandas.read_csv(file)
ops = pandas.DataFrame(df)
nato_phonetic_alphabet = {row.letter:row.code for (index,row) in ops.iterrows()}
#* 2. Create a list of the phonetic code words from a word that the user inputs.
def ask_for_word():
    word = input("Enter a word: ").upper()
    try:
        output_list = [nato_phonetic_alphabet[letter] for letter in word]
    except KeyError:
        print("Sorry, only letters in the alphabet please.")
        word = ask_for_word()
    else:
        print(output_list)

ask_for_word()

