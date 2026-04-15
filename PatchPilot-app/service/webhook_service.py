from fastapi import Request, HTTPException
import hmac
import hashlib
import time
import jwt
import requests

from utils.config_utils import ConfigUtils
from models.github_request import GitHubEventRequest
from utils.payload_parser import parse_github_event

def _verify_signature(payload: bytes, signature: str) -> bool:
    mac = hmac.new(ConfigUtils.get("GITHUB_WEBHOOK_SECRET").encode(), payload, hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)

def _generate_jwt():
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

def _get_installation_token():
    jwt_token = _generate_jwt()
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

async def github_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not _verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event= request.headers.get("X-GitHub-Event")
    payload = await request.json()

    parsed_request: GitHubEventRequest = parse_github_event(event, payload)

    # Send to orchestrator here and have it take care of the rest

    return {"message": "Received Payload"}
