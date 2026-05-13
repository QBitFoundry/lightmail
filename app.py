import asyncio
import threading
from flask import Flask, render_template_string, render_template
from aiosmtpd.controller import Controller
from flask_mail import Mail, Message
from datetime import datetime
import os
from dotenv import load_dotenv
if os.name != "nt":
    import fcntl

load_dotenv()

app = Flask(__name__)

received_mail: list[:object] = []

class MailHandler:
    async def handle_DATA(self, server, session, envelope):
        data = {
            "from": envelope.mail_from,
            "to": envelope.rcpt_tos,
            "body": envelope.content.decode("utf-8")
        }

        received_mail.append(data)

        return "250 ok"
    

@app.route('/')
def index():

    start_time = datetime.now()
    return render_template("index.html", emails=received_mail, start_time=start_time)

app.config['MAIL_SERVER'] = os.getenv("SMTP_IP")
app.config['MAIL_PORT'] = os.getenv("SMTP_PORT")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False

@app.route('/send_mail')
def send_mail():
    mail = Mail(app)
    message = Message("Test mail title",
                      sender="sender_test_mail@test.com",
                      recipients=["recipient_test_mail@test.com"])
    
    message.body = "This is a test mail message body."
    try:
        mail.send(message)
        return "Email sent!"
    except Exception as error:
        return f"Failed {str(error)}"
    

@app.route('/clear_mail')
def clear_mail():
    received_mail.clear()
    return "Mail cleared!"

def run_smtpd():
    handler: MailHandler = MailHandler()
    host: str = os.getenv("SMTP_IP")
    port: int = int(os.getenv("SMTP_PORT"))
    controller = Controller(handler, hostname=host, port=port)
    controller.start()
    print("SMTP server started on", host+":"+str(port))

def start_smtpd():
    smtp_thread = threading.Thread(target=run_smtpd, daemon=True)
    smtp_thread.start()

def smtpd_process_lock():
    if os.name != "nt":
        path = "/tmp/light-mail"
        os.makedirs(path, exist_ok=True)
        lock_file = open("/tmp/light-mail/smtp.lock", "w")
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            start_smtpd()
        except BlockingIOError:
            pass
    else:
        start_smtpd()

smtpd_process_lock()

if __name__ == "__main__":
    app.run(host=os.getenv("HOST_IP"), port=int(os.getenv("HOST_PORT")))