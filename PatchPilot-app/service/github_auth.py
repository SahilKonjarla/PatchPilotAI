import logging
import time

import jwt
import requests

from utils.config_utils import ConfigUtils

logger = logging.getLogger(__name__)
config = ConfigUtils()


def generate_jwt():
    app_id = config.get("GITHUB_APP_ID")
    private_key_path = config.get("GITHUB_PRIVATE_KEY_PATH")

    try:
        with open(private_key_path, "r") as f:
            private_key = f.read()
    except OSError as exc:
        logger.exception("Failed to read GitHub App private key from path=%s", private_key_path)
        raise RuntimeError("Failed to read GitHub App private key") from exc

    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": app_id
    }

    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    return encoded_jwt


def get_installation_token(installation_id: int):
    if not installation_id:
        raise ValueError("installation_id is required to create a GitHub installation token")

    jwt_token = generate_jwt()

    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }

    logger.info("Requesting GitHub installation token for installation_id=%s", installation_id)
    try:
        response = requests.post(url, headers=headers, timeout=20)
    except requests.RequestException as exc:
        logger.exception("GitHub installation token request failed")
        raise RuntimeError("Failed to request GitHub installation token") from exc

    if response.status_code != 201:
        logger.error(
            "GitHub installation token request failed status=%s body=%s",
            response.status_code,
            response.text,
        )
        raise RuntimeError(f"Failed to get installation token: {response.status_code}")

    token = response.json().get("token")
    if not token:
        raise RuntimeError("GitHub installation token response did not include token")

    return token
