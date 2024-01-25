import smtplib, datetime, random
from credentials import my_email, password, test_email

current_date = datetime.datetime.now()
file = "./quotes.txt"
quotes  = []
with open(file=file ,mode="r") as file:
    quotes = file.readlines()
index = random.randint(0, len(quotes))
if current_date.weekday() == 3:
    with smtplib.SMTP("smtp.gmail.com",  port=587) as conn:
        conn.starttls()
        conn.login(user=my_email, password=password)
        conn.sendmail(
            from_addr=my_email, 
            to_addrs=test_email, 
            msg=f"Subject:Motivational Quote\n\n{quotes[index]}")

