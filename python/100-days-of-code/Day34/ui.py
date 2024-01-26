from typing import Any, Optional, Tuple, Union
import customtkinter as ctk
from PIL import Image
from customtkinter.windows.widgets.font import CTkFont
from customtkinter.windows.widgets.image import CTkImage
THEME_COLOR = "#375362"

class QuizInterface(ctk.CTk):
    def __init__(self, **kwargs):
        super().__init__(fg_color=THEME_COLOR, **kwargs)
        self.title("Quiz IT!")
        self.geometry("500x900")
        self.grid_columnconfigure((0,1), weight=1)
        self.resizable(False,False)
        self.score = 0
        self.question = ""
        self.score_label = ctk.CTkLabel(master=self, text=f"Score: {self.score}/10", font=("courier new",40,"italic"), text_color="white")
        self.score_label.grid(row=0, column=0, columnspan=2, sticky="e", padx=(0,30), pady=(30,0))
        self.question_area = ctk.CTkLabel(master=self, text=f"{self.question}", width=200, height=400, fg_color="white", text_color="black", font=("courier new", 20,"bold"), wraplength=300)
        self.question_area.grid(row=1,column=0, sticky="we", columnspan=2, padx=50, pady=70)
        self.red_button = Button(master=self, button_img="./images/false.png", fg_color=THEME_COLOR, text="",hover = False)
        self.red_button.grid(row=3,column=0, sticky="nesw",pady=(40,0))
        self.green_button = Button(master=self, button_img="./images/true.png", fg_color=THEME_COLOR, text="",hover = False)
        self.green_button.grid(row=3, column=1, sticky="nesw",pady=(40,0))
    
    def update_quiz(self, score, question):
        self.score = score
        self.question = question
        self.score_label.configure(text=f"Score: {self.score}/10")
        self.question_area.configure(text=f"{self.question}")

class Button(ctk.CTkButton):
    def __init__(self, button_img, width=100, height=99,**kwargs):
        super().__init__(**kwargs)
        self.btn_img = ctk.CTkImage(Image.open(button_img), size=(100,99))
        self.configure(image= self.btn_img)