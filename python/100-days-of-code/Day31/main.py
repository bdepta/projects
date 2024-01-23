from frame import App, Button, Frame, BACKGROUND_COLOR
import time, pandas, random

app = App()
# # app.flashcard.show_back()

data = pandas.read_csv("/Users/z0051309/Downloads/french_words.csv")
data_dict = data.to_dict()
print(data)
print(data_dict)


index = random.randint(0,len(data_dict["French"].items())-1)
french_word = data_dict['French'][index]
english_word = data_dict['English'][index]

app.flashcard = Frame(master=app, corner_radius=0, fg_color=BACKGROUND_COLOR)
app.flashcard.grid(row=0, column=0, columnspan=2, rowspan = 2, sticky="nesw", padx=50, pady=50)
app.red_button = Button(master=app, button_img="./images/wrong.png", fg_color=BACKGROUND_COLOR, text="",hover = False)
app.red_button.grid(row=1, column=0, sticky="nesw",pady=(40,0))
app.green_button = Button(master=app, button_img="./images/right.png", fg_color=BACKGROUND_COLOR,hover = False,  text="")
app.green_button.grid(row=1, column=1, sticky="nesw",pady=(40,0))

app.flashcard.show_front(french_word=french_word)
# time.sleep(3)
# app.flashcard.show_back(english_word=english_word)

app.mainloop()


