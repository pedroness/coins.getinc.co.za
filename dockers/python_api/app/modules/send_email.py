import email, smtplib, ssl
from fastapi import Depends, HTTPException, status
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import env

env_var = env().env


class sm:
    def __init__(self, to, subject, sender_email=None):
        if sender_email is None:
            print(env_var["PY_EMAIL_FROM"])
            sender_email = env_var["PY_EMAIL_FROM"]
        self.auth_email = env_var["PY_EMAIL_USER"]
        self.sender_email = env_var["PY_EMAIL_FROM"]
        self.smtp = env_var["PY_EMAIL_HOST"]
        self.port = env_var["PY_EMAIL_PORT"]
        self.password = env_var["PY_EMAIL_PASSWORD"]
        self.message = MIMEMultipart("alternative")
        self.message["From"] = sender_email
        self.message["To"] = to
        self.message["Subject"] = subject

    def buildmail(self, body=None):
        if body is None:
            body = self.message["Subject"]
        # Create the plain-text and HTML version of your message
        text = ""
        html = body

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        self.message.attach(part1)
        self.message.attach(part2)

        return True

    def addattachments(self, attachments):

        self.attachments = attachments

        for filename in self.attachments:
            try:
                # Open PDF file in binary mode
                with open(filename, "rb") as attachment:
                    # Add file as application/octet-stream
                    # Email client can usually download this automatically as attachment
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                # Encode file in ASCII characters to send by email
                encoders.encode_base64(part)

                # Add header as key/value pair to attachment part
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
                )

                # Add attachment to message and convert message to string
                self.message.attach(part)
            except (Exception, Error) as error:
                print("Error while connecting to PostgreSQL", error)
                raise Error
        return True

    def send(self):
        try:
            context = ssl.create_default_context()
            print(self.smtp,self.auth_email,self.password)
            with smtplib.SMTP_SSL(self.smtp, self.port, context=context) as server:
                server.login(self.auth_email, self.password)
                server.sendmail(
                    self.message["From"], self.message["To"], self.message.as_string()
                )
        except (Exception) as error:
            print(error)
            raise HTTPException(
            status_code=403,
            detail="Error sending email",
            ) 
        return True
