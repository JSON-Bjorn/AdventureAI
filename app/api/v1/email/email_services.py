# External imports
import requests
from fastapi import HTTPException

# Internal imports
from app.api.logger.loggable import Loggable
from app.settings import Settings


class EmailServices(Loggable):
    def __init__(self):
        super().__init__()
        self.logger.info("Email services initialized")

    def send_activation_email(self, email: str, token: str):
        response = requests.post(
            Settings.MAILGUN_DOMAIN,
            auth=(
                "api",
                Settings.MAILGUN_API_KEY,
            ),
            data={
                "from": f"Mailgun Sandbox <{Settings.MAILGUN_EMAIL}>",
                "to": email,
                "subject": "Adventure AI activation link",
                "text": f"Click the link below to activate your account:\n{Settings.FRONTEND_URL}/verify_token/{token}",
            },
        )

        if response.status_code != 200:
            self.logger.error(
                f"Failed to send activation email: {response.text}"
            )
            raise HTTPException(
                status_code=500, detail="Failed to send activation email"
            )
