import base64
from sendgrid import SendGridAPIClient, Attachment, FileContent, FileName, FileType, Disposition
from sendgrid.helpers.mail import Mail


class SendgridService:
    @staticmethod
    def send_email(
        from_email: str,
        to_emails: list,
        subject: str,
        attachment: str,
        api_key: str
    ) -> None:
        message = Mail(
            from_email=from_email,
            to_emails=to_emails,
            subject=subject,
            html_content=subject
        )
        try:
            with open(attachment, 'rb') as f:
                data = f.read()
                f.close()
            encoded_file = base64.b64encode(data).decode()

            attached_file = Attachment(
                FileContent(encoded_file),
                FileName(attachment),
                FileType('application/xlsx'),
                Disposition('attachment')
            )
            message.attachment = attached_file

            sg = SendGridAPIClient(api_key)
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)