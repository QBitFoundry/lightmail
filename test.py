import smtplib

def test_email_sending():
    smtp = smtplib.SMTP("127.0.0.1", 8025)

    smtp.sendmail(
        "test@email.com",
        ["receive@email.com"],
        "Subject: Test Hello"
    )

    smtp.quit()
    