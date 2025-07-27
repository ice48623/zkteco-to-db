import base64
import brevo_python
from brevo_python.rest import ApiException
from pprint import pprint


class BrevoService:
    @staticmethod
    def send_email(
            from_email: str,
            to_emails: list,
            subject: str,
            message: str,
            attachment_name: str,
            attachment_path: str,
            api_key: str
    ):
        configuration = brevo_python.Configuration()
        configuration.api_key['api-key'] = api_key
        api_instance = brevo_python.TransactionalEmailsApi(brevo_python.ApiClient(configuration))

        with open(attachment_path, 'rb') as f:
            attachment_content = base64.b64encode(f.read()).decode('utf-8')

        attachment = {
            "name": attachment_name,
            "content": attachment_content
        }

        send_smtp_email = brevo_python.SendSmtpEmail(
            to=to_emails,
            bcc=None,
            cc=None,
            reply_to=None,
            headers=None,
            html_content=message,
            sender=from_email,
            subject=subject,
            attachment=[attachment]
        )

        try:
            # Send a transactional email
            api_response = api_instance.send_transac_email(send_smtp_email)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling TransactionalEmailsApi->send_transac_email: %s\n" % e)
