from typing import Any, Optional, Tuple, Union
from quiz_brain import QuizBrain
import customtkinter as ctk
from PIL import Image
from customtkinter.windows.widgets.font import CTkFont
from customtkinter.windows.widgets.image import CTkImage
THEME_COLOR = "#375362"

class QuizInterface(ctk.CTk):
    def __init__(self, quiz_brain: QuizBrain,**kwargs):
        super().__init__(fg_color=THEME_COLOR, **kwargs)
        self.quiz = quiz_brain
        self.title("Quiz IT!")
        self.geometry("500x900")
        self.grid_columnconfigure((0,1), weight=1)
        self.resizable(False,False)
        self.score_label = ctk.CTkLabel(master=self, text=f"Score: 0/10", font=("courier new",40,"italic"), text_color="white")
        self.score_label.grid(row=0, column=0, columnspan=2, sticky="e", padx=(0,30), pady=(30,0))
        self.question_area = ctk.CTkLabel(master=self, text=f"", width=200, height=400, fg_color="white", text_color="black", font=("courier new", 20,"bold"), wraplength=300)
        self.question_area.grid(row=1,column=0, sticky="we", columnspan=2, padx=50, pady=70)
        self.red_button = Button(master=self, button_img="./images/false.png", fg_color=THEME_COLOR, text="",hover = False, command=self.red_button_action)
        self.red_button.grid(row=3,column=0, sticky="nesw",pady=(40,0))
        self.green_button = Button(master=self, button_img="./images/true.png", fg_color=THEME_COLOR, text="",hover = False, command=self.green_button_action)
        self.green_button.grid(row=3, column=1, sticky="nesw",pady=(40,0))
        self.get_next_question()
        self.mainloop()
    
    def get_next_question(self):
        self.question_area.configure(fg_color="white")
        if self.quiz.still_has_questions():
            q_text = self.quiz.next_question()
            score = self.quiz.score
            self.question_area.configure(text=f"{q_text}")
            self.score_label.configure(text=f"Score: {score}/10")
        else:
            self.question_area.configure(text="You've reached the end of quiz. Check your score in top right corner.")
            self.red_button.configure(command=None)
            self.green_button.configure(command=None)
    def green_button_action(self):
        self.feedback(self.quiz.check_answer(user_answer="True"))
    
    def red_button_action(self):
        is_right = self.quiz.check_answer(user_answer="False")
        self.feedback(is_right)

    def feedback(self, is_right):
        if is_right:
            self.question_area.configure(fg_color="green")
        else:
            self.question_area.configure(fg_color="red")
        self.after(1000, self.get_next_question)
        

class Button(ctk.CTkButton):
    def __init__(self, button_img, width=100, height=99,**kwargs):
        super().__init__(**kwargs)
        self.btn_img = ctk.CTkImage(Image.open(button_img), size=(100,99))
        self.configure(image= self.btn_img)