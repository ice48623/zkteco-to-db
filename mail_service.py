import smtplib
import ssl
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class MailService:
    @staticmethod
    def send_mail(to_email: str, subject: str, message: str, attachments: list, host: str, port: int, from_email: str, app_password: str):
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        for filepath in attachments:
            part = MIMEBase('application', "octet-stream")
            with open(filepath, 'rb') as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            'attachment; filename={}'.format(Path(filepath).name))
            msg.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=context) as s:
            s.login(from_email, app_password)
            s.sendmail(from_email, to_email, msg.as_string())
