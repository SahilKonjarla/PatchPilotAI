from fastapi import Request, HTTPException
import hmac
import hashlib

from utils.config_utils import ConfigUtils
from models.github_request import GitHubEventRequest
from utils.payload_parser import parse_github_event

def _verify_signature(payload: bytes, signature: str) -> bool:
    mac = hmac.new(ConfigUtils.get("GITHUB_WEBHOOK_SECRET").encode(), payload, hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)

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
