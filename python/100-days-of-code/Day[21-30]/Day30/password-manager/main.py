from tkinter import *
from tkinter import messagebox
import random
import pyperclip
import customtkinter
import json

OUTPUT_FILE = "./data.json"

# ---------------------------- PASSWORD GENERATOR ------------------------------- #

def generate_password():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    nr_letters = random.randint(8, 10)
    nr_symbols = random.randint(2, 4)
    nr_numbers = random.randint(2, 4)


    password_letters = [random.choice(letters) for _ in range(nr_letters)]
    password_symbols = [random.choice(symbols) for _ in range(nr_symbols)]
    password_numbers = [random.choice(numbers) for _ in range(nr_numbers)]

    password_list = password_letters + password_symbols + password_numbers

    random.shuffle(password_list)

    X = "".join(password_list)
    password_entry.insert(0, X)
    pyperclip.copy(X)

# ---------------------------- SAVE PASSWORD ------------------------------- #

def save_password():
    website = website_entry.get().lower()
    username = username_entry.get()
    password = password_entry.get()
    new_data ={website:
               {
                   "email": username,
                   "password" : password
               }}
    if len(website) == 0 or len(username) == 0 or len(password) == 0:
        messagebox.showerror(title="ERROR", message="One of the fields is empty.")
    else:
        try: 
            with open(OUTPUT_FILE, mode='r') as file:
                data =json.load(file)
                data.update(new_data)
        except FileNotFoundError:
            with open(OUTPUT_FILE, mode='w') as file:
                json.dump(new_data, file, indent=4)
        else:    
            with open(OUTPUT_FILE, mode='w') as file:
                json.dump(data, file, indent=4)
        finally:
            website_entry.delete(0, END)
            password_entry.delete(0, END)

# ---------------------------- SAVE PASSWORD ------------------------------- #

def search_password():
    website = website_entry.get().lower()
    try: 
        with open(OUTPUT_FILE, mode='r') as file:
            data = json.load(file)     
    except FileNotFoundError:
            messagebox.showinfo(title="NO DATA", message="Your password file is empty.")
    else:
       if website in data:
           messagebox.showinfo(title=f"Credentials for {website}", message=f"Username: {data[website]['email']}\nPassword: {data[website]['password']}")
       else:
           messagebox.showinfo(title=f"Credentials for {website}", message=f"There are no credentials for: {website}")
    finally:
        website_entry.delete(0, END)
        password_entry.delete(0, END)

# ---------------------------- UI SETUP ------------------------------- #

window = customtkinter.CTk()
window.title("Password Manager")
window.config(padx=50, pady=50, bg="black")
window.resizable(False,False)
window.grid_columnconfigure(0, weight=1)
lock_img = PhotoImage(file="./logo.png")

image_label = customtkinter.CTkCanvas(width=200, height=200, bg="black", highlightthickness=0)
image_label.create_image(100,100, image=lock_img)
image_label.grid(row=0, column=1)


website_label = customtkinter.CTkLabel(window, text="Website: ", bg_color="black")
website_label.grid(row=1, column=0, sticky="e")


website_entry = customtkinter.CTkEntry(window, width=21)
website_entry.grid(row=1, column=1 , padx=10, sticky="ew")
website_entry.focus()
website_search = customtkinter.CTkButton(window, text="Search", command=search_password)
website_search.grid(row=1, column=2, sticky="e", padx=10, pady=10)

username_label = customtkinter.CTkLabel(window, text="Email/Username: ", bg_color="black")
username_label.grid(row=2, column=0, sticky="e")

username_entry = customtkinter.CTkEntry(window, width=35)
username_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=10)
username_entry.insert(index=0, string="b.depta@icloud.com")

password_label = customtkinter.CTkLabel(window, text="Password: ", bg_color="black")
password_label.grid(row=3, column=0, sticky="e")

password_entry =customtkinter.CTkEntry(window, width=21)
password_entry.grid(row=3, column=1, sticky="ew", padx=10)

password_button = customtkinter.CTkButton(window, text="Generate Password", command=generate_password)
password_button.grid(row=3, column=2, sticky="e", padx=10, pady=10)

add_button = customtkinter.CTkButton(window, text="Add", command=save_password, width=36)
add_button.grid(row=4, column=1, columnspan=2, sticky="ew", padx=10)

window.mainloop()