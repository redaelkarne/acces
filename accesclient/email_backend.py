import msal
import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

class MicrosoftGraphEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.tenant_id = settings.AZURE_TENANT_ID
        self.client_id = settings.AZURE_CLIENT_ID
        self.client_secret = settings.AZURE_CLIENT_SECRET
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]

    def get_access_token(self):
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret,
        )
        result = app.acquire_token_for_client(scopes=self.scope)
        if "access_token" in result:
            return result["access_token"]
        else:
            if not self.fail_silently:
                print(f"Error acquiring token: {result.get('error')}")
                print(f"Error description: {result.get('error_description')}")
            return None

    def send_messages(self, email_messages):
        token = self.get_access_token()
        if not token:
            return 0

        count = 0
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        for message in email_messages:
            if self._send(message, headers):
                count += 1
        return count

    def _send(self, email_message, headers):
        # Ensure we have a sender
        from_email = email_message.from_email or settings.DEFAULT_FROM_EMAIL
        
        # Prepare recipients
        to_recipients = [{"emailAddress": {"address": addr}} for addr in email_message.to]
        cc_recipients = [{"emailAddress": {"address": addr}} for addr in email_message.cc]
        bcc_recipients = [{"emailAddress": {"address": addr}} for addr in email_message.bcc]
        
        # Prepare body
        content_type = "HTML" if email_message.content_subtype == "html" else "Text"
        body_content = email_message.body
        
        # Check for alternatives (e.g. HTML)
        if hasattr(email_message, 'alternatives') and email_message.alternatives:
            for content, mimetype in email_message.alternatives:
                if mimetype == 'text/html':
                    content_type = "HTML"
                    body_content = content
                    break
        
        email_content = {
            "message": {
                "subject": email_message.subject,
                "body": {
                    "contentType": content_type,
                    "content": body_content
                },
                "toRecipients": to_recipients,
                "ccRecipients": cc_recipients,
                "bccRecipients": bcc_recipients
            },
            "saveToSentItems": "false"
        }

        # Endpoint: /users/{id | userPrincipalName}/sendMail
        endpoint = f"https://graph.microsoft.com/v1.0/users/{from_email}/sendMail"
        
        try:
            response = requests.post(endpoint, headers=headers, json=email_content)
            if response.status_code == 202:
                return True
            else:
                if not self.fail_silently:
                    print(f"Error sending email to {endpoint}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            if not self.fail_silently:
                print(f"Exception sending email: {e}")
            return False
