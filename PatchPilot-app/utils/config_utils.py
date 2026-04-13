import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()  # loads .env if present

class ConfigUtils:
    def __init__(self):
        REQUIRED_KEYS = [
            "GITHUB_APP_ID",
            "GITHUB_CLIENT_ID",
            "GITHUB_CLIENT_SECRET",
            "GITHUB_WEBHOOK_SECRET",
            "GITHUB_API_TOKEN",
            "GITHUB_PRIVATE_KEY_PATH",
            "GITHUB_PRIVATE_KEY",
            "OPENAI_API_KEY",
            "OPENAI_MODEL",
            "OPENAI_BASE_URL",
        ]
        # Create a dictionary to store them
        self.env_vars = {}

        for key in REQUIRED_KEYS:
            value = os.getenv(key)
            if not value:
                raise EnvironmentError(f"Environment variable '{key}' not set")
            self.env_vars[key] = value

    def get(self, key: str) -> Any | None:
        """
        Retrieve a specific environment variable by key.
        """
        return self.env_vars.get(key)
