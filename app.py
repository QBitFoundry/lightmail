import asyncio
import threading
from flask import Flask, render_template_string, render_template
from aiosmtpd.controller import Controller
from flask_mail import Mail, Message
from datetime import datetime
import os
from dotenv import load_dotenv
import json

if os.name != "nt":
    import fcntl
try:
    import uwsgi
    HAS_UWSGI = True
    # uwsgi.lock()
except ImportError:
    HAS_UWSGI = False

import time

load_dotenv()

app = Flask(__name__)


class UwsgiSharedData:
    def get(self) -> list[dict]:
        data: list[dict] = []
        if HAS_UWSGI:
            uwsgi.lock()
            try:
                uwsgi_cache_data = uwsgi.cache_get("received_mail", "light_mail")
                if uwsgi_cache_data is not None:
                    data = json.loads(uwsgi_cache_data)
            finally:
                uwsgi.unlock()
        return data

    def set(self, data) -> None:
        if HAS_UWSGI:
            try:
                uwsgi.lock()
                if len(data) > 100:
                    data = data[-100:]
                uwsgi.cache_update("received_mail", json.dumps(data), 0, "light_mail")
            finally:
                uwsgi.unlock()


uwsgi_shared_data = UwsgiSharedData()
received_mail: list[dict] = []


class MailHandler:
    async def handle_DATA(self, server, session, envelope):
        data = {
            "from": envelope.mail_from,
            "to": envelope.rcpt_tos,
            "body": envelope.content.decode("utf-8")
        }

        received_mail = uwsgi_shared_data.get()
        received_mail.append(data)
        uwsgi_shared_data.set(received_mail)

        return "250 ok"
    

@app.route('/')
def index():
    
    start_time = datetime.now()
    received_mail = uwsgi_shared_data.get()
    return render_template("index.html", emails=received_mail, start_time=start_time)


app.config['MAIL_SERVER'] = os.getenv("HOST_IP") # SMTP_IP
app.config['MAIL_PORT'] = int(os.getenv("SMTP_PORT"))
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = None
app.config['MAIL_PASSWORD'] = None
app.config['MAIL_SUPPRESS_SEND'] = False

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
    received_mail = uwsgi_shared_data.get()
    received_mail.clear()
    uwsgi_shared_data.set(received_mail)
    return "Mail cleared!"

def run_smtpd():
    handler: MailHandler = MailHandler()
    host: str = os.getenv("HOST_IP") # SMTP_IP
    port: int = int(os.getenv("SMTP_PORT"))
    controller = Controller(handler, hostname=host, port=port)
    controller.start()
    print("SMTP server started on", host+":"+str(port))

    try:
        while True:
            time.sleep(1)
    finally:
        controller.stop()

def start_smtpd():
    smtp_thread = threading.Thread(target=run_smtpd, daemon=True)
    smtp_thread.start()

def smtpd_process_lock():
    if os.name != "nt":
        path = "/tmp/light-mail"
        os.makedirs(path, exist_ok=True)
        # NOTE: Use db.sqlite3 as file to lock and for persistent storage.❌
        lock_file = open("/tmp/light-mail/smtp.lock", "w")
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            start_smtpd()
        except BlockingIOError:
            pass
    else:
        start_smtpd()

if HAS_UWSGI:
    uwsgi.post_fork_hook = smtpd_process_lock
    # uwsgi.unlock()
else:
    smtpd_process_lock()

if __name__ == "__main__":
    app.run(host=os.getenv("HOST_IP"), port=int(os.getenv("HOST_PORT")), debug=False)
