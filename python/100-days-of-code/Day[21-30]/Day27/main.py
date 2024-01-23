import tkinter

window = tkinter.Tk()
window.title("Mile to Km Converter")
window.minsize(width=350, height=100)
window.config(padx=0,pady=20)

def button_clicked():
    new_text = entry.get()
    calc = float(new_text)*1.61
    label4["text"] = calc
    

label1 = tkinter.Label(text="")
label1.config(width=20)
label1.grid(column=0,row=0)
entry = tkinter.Entry(justify='center')
entry.grid(column=1,row=0)
button = tkinter.Button()
label2 = tkinter.Label(text="Miles", font=("Arial",10,"italic"))
label2.grid(column=2,row=0)
label2.config(padx=20)
label3 = tkinter.Label(text="is equal to", font=("Arial",10,"italic"))
label3.grid(column=0,row=1)
label3.config(padx=20)
label4 = tkinter.Label(text="0", font=("Arial",10,"italic"))
label4.anchor("center")
label4.grid(column=1,row=1)
label2 = tkinter.Label(text="Km", font=("Arial",10,"italic"))
label2.grid(column=2,row=1)
label2.config(padx=20)
label6 = tkinter.Label(text="")
label6.config(width=20)
label6.grid(column=0,row=2)
button1 = tkinter.Button(text="Calculate", command=button_clicked)
button1.grid(column=1, row=2)
window.mainloop()