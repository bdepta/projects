from tkinter import *
import math
# ---------------------------- CONSTANTS ------------------------------- #
BEIGE = "#FFF8E3"
PINK = "#E6A4B4"
PEACH = "#F3D7CA"
GRAY = "#F5EEE6"
FONT_NAME = "Courier"
WORK_MIN = 1
SHORT_BREAK_MIN = 1
LONG_BREAK_MIN = 20
REPS = 0
G_CHECK= "✓"
TIMER = None
# ---------------------------- TIMER RESET ------------------------------- # 
def reset_timer():
    global REPS
    window.after_cancel(TIMER)
    canvas.itemconfig(timer_text, text=f'25:00')
    timer_label["text"] = "Timer"
    check_label["text"] = None
    REPS = 0
# ---------------------------- TIMER MECHANISM ------------------------------- # 

def start_timer():
    start_button.destroy()
    button = Button(text="Start", bg=PEACH, borderwidth=0)
    button.grid(column=0, row=2)
    global REPS
    REPS += 1
    if REPS % 2 == 0:
        timer_label["text"] = "SHORT BREAK"
        timer_label["fg"] = PINK
        count_down(SHORT_BREAK_MIN*60)
    if REPS % 2 == 0 and REPS % 8 == 0:
        timer_label["text"] = "LONG BREAK"
        timer_label["fg"] = PEACH
        count_down(LONG_BREAK_MIN*60)
    if REPS % 2 != 0:
        timer_label["text"] = "WORK"
        timer_label["fg"] = "#116A7B"
        count_down(WORK_MIN*60)

# ---------------------------- COUNTDOWN MECHANISM ------------------------------- # 

def count_down(count):
    global REPS, G_CHECK, TIMER
    count_min = math.floor(count / 60)
    count_sec = count % 60
    if count_sec < 10:
        count_sec = f'0{count_sec}'
    canvas.itemconfig(timer_text, text=f'{count_min}:{count_sec}')
    if count > 0:
        TIMER = window.after(1000, count_down, count - 1)

    else:
        start_timer()
        if REPS % 2 != 0:
            check_label["text"] += G_CHECK
# ---------------------------- UI SETUP ------------------------------- #



window = Tk()
window.title("Pomodoro Timer")
window.config(padx=90,pady=45, bg=BEIGE)
timer_label = Label(text="Timer", fg=PINK, font=(FONT_NAME, 40, "italic"), bg=BEIGE)
timer_label.grid(column=1, row=0)
canvas = Canvas(width=200,height=224, bg=BEIGE, highlightthickness=0)
tomato_img = PhotoImage(file="./tomato.png")
canvas.create_image(100,110, image=tomato_img)
timer_text = canvas.create_text(103,130, text="25:00", fill=GRAY, font=(FONT_NAME, 35, "bold"))
canvas.grid(column=1, row=1)
start_button = Button(text="Start", bg=PEACH, borderwidth=0, command=start_timer)
start_button.grid(column=0, row=2)
reset_button = Button(text="Reset", bg=PEACH, borderwidth=0, command=reset_timer)
reset_button.grid(column=2, row=2)
check_label = Label(fg=PINK,bg=BEIGE, font=(FONT_NAME, 15, "bold"))
check_label.grid(column=1, row=3)
window.mainloop()