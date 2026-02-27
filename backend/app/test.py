import smtplib

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login("shreehari.wpadummy98@gmail.com", "fncknjwzkcofrmgc")

server.sendmail(
    "shreehari.wpadummy98@gmail.com",
    "shreehari.wpa@gmail.com",
    "Subject: Test Email\n\nThis is a test."
)

print("Email sent successfully")
server.quit()