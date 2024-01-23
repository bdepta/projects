import tkinter

window = tkinter.Tk()
window.title("Hello World")
window.minsize(width=500, height=500)
def button_clicked():
    show = user_input.get()
    my_label["text"] = show
my_label = tkinter.Label(text="I am a label", font=("Arial",24,"italic"))
my_label.grid(column=0, row=0)
button1 = tkinter.Button(text="Click me.", command=button_clicked)
button1.grid(column=1, row=1)
button2 = tkinter.Button(text="Click me.", command=button_clicked)
button2.grid(column=3, row=0)
user_input = tkinter.Entry()
user_input.grid(column=4, row=2)






window.mainloop()