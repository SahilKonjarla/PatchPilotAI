import time
import jwt
import requests

from utils.config_utils import ConfigUtils

def generate_jwt():
    app_id = ConfigUtils.get("GITHUB_APP_ID")
    private_key_path = ConfigUtils.get("GITHUB_PRIVATE_KEY_PATH")

    with open(private_key_path, "r") as f:
        private_key = f.read()

    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": app_id
    }

    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    return encoded_jwt

def get_installation_token():
    jwt_token = generate_jwt()
    install_id = ConfigUtils.get("GITHUB_INSTALL_ID")

    url = f"https://api.github.com/app/installations/{install_id}/access_tokens"

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.post(url, headers=headers)

    if response.status_code != 201:
        raise Exception(f"Failed to get installation token: {response.text}")

    return response.json()["token"]