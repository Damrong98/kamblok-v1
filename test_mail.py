# test_smtp.py
import smtplib

smtp_server = "smtp.gmail.com"
port = 587
username = "damrong.work98@gmail.com"
password = "nqygbiapntclnfoj"  # No spaces

try:
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(username, password)
    print("Login successful!")
    server.quit()
except Exception as e:
    print(f"Error: {e}")