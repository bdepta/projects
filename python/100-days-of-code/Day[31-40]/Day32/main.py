from excercises.credentials import my_email, password
import random, smtplib,datetime, pandas

current_date = datetime.datetime.now()
data = pandas.read_csv("./birthdays.csv")

for index , row in data.iterrows():
    if row["month"] == current_date.month and row["day"] == current_date.day:
        letter_list = ["./letter_templates/letter_1.txt","./letter_templates/letter_2.txt","./letter_templates/letter_3.txt"]
        choice_letter = random.choice(letter_list)
        with open(choice_letter, mode="r") as file:
            letter = file.read()
        personal_letter = letter
        personal_letter = personal_letter.replace("[NAME]", row["name"])
        with smtplib.SMTP("smtp.gmail.com",  port=587) as conn:
            conn.starttls()
            conn.login(user=my_email, password=password)
            conn.sendmail(
                from_addr=my_email, 
                to_addrs=row["email"], 
                msg=f"Subject:Happy Birthdays!\n\n{personal_letter}")





