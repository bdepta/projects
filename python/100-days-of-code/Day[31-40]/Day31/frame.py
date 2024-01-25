from tkinter import Variable
from typing import Any, Callable, Optional, Tuple, Union
import customtkinter
from PIL import Image, ImageTk
import time, pandas, random
from customtkinter.windows.widgets.font import CTkFont
from customtkinter.windows.widgets.image import CTkImage


BACKGROUND_COLOR = "#B1DDC6"


class Frame(customtkinter.CTkFrame):
    def __init__(self,french_word,english_word,master: Any, width: int = 800, height: int = 526, corner_radius: int | str | None = None, border_width: int | str | None = None, bg_color: str | Tuple[str, str] = "transparent", fg_color: str | Tuple[str, str] | None = None, border_color: str | Tuple[str, str] | None = None, background_corner_colors: Tuple[str | Tuple[str, str]] | None = None, overwrite_preferred_drawing_method: str | None = None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        self.grid_columnconfigure((0,1), weight=1)
        self.imgs = ["./images/card_front.png","./images/card_back.png"]
        self.current_index = 1
        self.french_word = french_word
        self.english_word = english_word
        self.define_canvas()
        
        # Define canvas for back and front of the flashcard.
    def define_canvas(self):
        if self.current_index%2 == 1:
            self.flashcard_img = customtkinter.CTkImage(Image.open(self.imgs[0]), size=(800,526))
            self.lang = "French"
            self.color = "white"
            self.word = self.french_word
            self.current_index += 1
        else:   
            self.flashcard_img = customtkinter.CTkImage(Image.open(self.imgs[1]), size=(800,526))
            self.lang = "English"
            self.color = "#91c2af"
            self.word = self.english_word
            self.current_index += 1
        self.bg_img_label = customtkinter.CTkLabel(self, text="", image=self.flashcard_img)
        self.bg_img_label.grid(row=0,column=0, rowspan=2)
        self.lang_label = customtkinter.CTkLabel(self, text=self.lang, fg_color=self.color,text_color="black", font=('Ariel',40,'italic'))
        self.lang_label.grid(row=0,column=0)
        self.word_label = customtkinter.CTkLabel(self, text=self.word,fg_color=self.color,text_color="black", font=('Ariel',60,'bold'))
        self.word_label.grid(row=1,column=0)
        self.after_id=self.after(3000, self.define_canvas)
        if self.current_index%2 == 1:
            self.after_cancel(self.after_id)
            
        




class Button(customtkinter.CTkButton):
    def __init__(self, button_img, width=100, height=99,**kwargs):
        super().__init__(**kwargs)
        self.btn_img = customtkinter.CTkImage(Image.open(button_img), size=(100,99))
        self.configure(image= self.btn_img)

class App(customtkinter.CTk):
    def __init__(self, fg_color= BACKGROUND_COLOR, **kwargs):
        super().__init__(fg_color = BACKGROUND_COLOR, **kwargs)
        self.geometry("900x800")
        self.grid_rowconfigure((0,2), weight=1)
        self.grid_columnconfigure((0,1), weight=1)
        self.resizable(False,False)
        self.open_source_file()
        self.next_word()
        

    def open_source_file(self):
        self.source_file = "./data/source_file.csv"
        self.to_learn_file = "./data/to_learn.csv"
        self.data = pandas.read_csv(self.source_file)
        try:
            self.to_learn = pandas.read_csv(self.to_learn_file)
        except:
            self.to_learn = pandas.read_csv(self.source_file)
            self.to_learn.to_csv(self.to_learn_file, index=False)
        self.data_dict = self.data.to_dict()
        self.to_learn_dict = self.to_learn.to_dict()

    def setup_flashcards(self):
        self.flashcard = Frame(master=self, corner_radius=0, fg_color=BACKGROUND_COLOR, english_word=self.english_word, french_word=self.french_word)
        self.flashcard.grid(row=0, column=0, columnspan=2, rowspan = 2, sticky="nesw", padx=50, pady=50)
        self.red_button = Button(master=self, button_img="./images/wrong.png", fg_color=BACKGROUND_COLOR, text="",hover = False, command=self.red_button_action)
        self.red_button.grid(row=1, column=0, sticky="nesw",pady=(40,0))
        self.green_button = Button(master=self, button_img="./images/right.png", fg_color=BACKGROUND_COLOR,hover = False,  text="", command=self.green_button_action)
        self.green_button.grid(row=1, column=1, sticky="nesw",pady=(40,0))

    def red_button_action(self):
        self.next_word()
    
    def green_button_action(self):
        self.to_learn = self.to_learn.drop(self.index, axis='index')
        self.to_learn.to_csv(self.to_learn_file, index=False)
        self.to_learn = pandas.read_csv(self.to_learn_file)
        self.to_learn_dict = self.to_learn.to_dict()
        self.next_word()

    def next_word(self):
        self.index = random.randint(0,len(self.to_learn_dict["French"].items())-1)
        self.french_word = self.to_learn_dict['French'][self.index]
        self.english_word = self.to_learn_dict['English'][self.index]
        self.setup_flashcards()
        
        
        