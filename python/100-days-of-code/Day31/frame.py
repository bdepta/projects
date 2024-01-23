from tkinter import Variable
from typing import Any, Callable, Optional, Tuple, Union
import customtkinter
from PIL import Image
import time
from customtkinter.windows.widgets.font import CTkFont
from customtkinter.windows.widgets.image import CTkImage


BACKGROUND_COLOR = "#B1DDC6"


class Frame(customtkinter.CTkFrame):
    def __init__(self,master: Any, width: int = 800, height: int = 526, corner_radius: int | str | None = None, border_width: int | str | None = None, bg_color: str | Tuple[str, str] = "transparent", fg_color: str | Tuple[str, str] | None = None, border_color: str | Tuple[str, str] | None = None, background_corner_colors: Tuple[str | Tuple[str, str]] | None = None, overwrite_preferred_drawing_method: str | None = None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        self.grid_columnconfigure((0,1), weight=1)
        self.define_canvas()
        
        # Define canvas for back and front of the flashcard.
    def define_canvas(self):
        self.canvas_img_front = "./images/card_front.png"
        self.canvas_img_back = "./images/card_back.png"
        self.flashcard_img_front = customtkinter.CTkImage(Image.open(self.canvas_img_front), size=(800,526))
        self.flashcard_img_back = customtkinter.CTkImage(Image.open(self.canvas_img_back), size=(800,526))
        
        # Display Front of the Flashcard.
    def show_front(self, french_word):
        self.bg_img_label = customtkinter.CTkLabel(self, text="", image=self.flashcard_img_front)
        self.bg_img_label.grid(row=0,column=0, rowspan=2)
        self.lang_label = customtkinter.CTkLabel(self, text="French", fg_color="white",text_color="black", font=('Ariel',40,'italic'))
        self.lang_label.grid(row=0,column=0)
        self.word_label = customtkinter.CTkLabel(self, text=french_word,fg_color="white",text_color="black", font=('Ariel',60,'bold'))
        self.word_label.grid(row=1,column=0)

    def show_back(self, english_word):
        self.bg_img_label.configure(image=self.flashcard_img_back)
        self.lang_label.configure(text="English",fg_color="#91c2af")
        self.word_label.configure(text=english_word, fg_color="#91c2af")

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

        # self.flashcard = Frame(master=self, corner_radius=0, bg_color=BACKGROUND_COLOR, fg_color=BACKGROUND_COLOR)
        
        
        