import pandas
#* 1. Create a dictionary in this format:
{"A": "Alfa", "B": "Bravo"}
file = "./nato_phonetic_alphabet.csv"
df = pandas.read_csv(file)
ops = pandas.DataFrame(df)
nato_phonetic_alphabet = {row.letter:row.code for (index,row) in ops.iterrows()}
#* 2. Create a list of the phonetic code words from a word that the user inputs.
word = input("Enter a word: ").upper()
output_list = [nato_phonetic_alphabet[letter] for letter in word]
print(output_list)

