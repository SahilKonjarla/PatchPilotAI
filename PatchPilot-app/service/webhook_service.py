from fastapi import Request, HTTPException
import hmac
import hashlib

from utils.config_utils import ConfigUtils
from models.github_request import GitHubEventRequest
from utils.payload_parser import parse_github_event
from agents.orchestrator_agent import Orchestrator

orchestrator = Orchestrator()
config = ConfigUtils()

def _verify_signature(payload: bytes, signature: str) -> bool:
    mac = hmac.new(config.get("GITHUB_WEBHOOK_SECRET").encode(), payload, hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)

async def github_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not _verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event= request.headers.get("X-GitHub-Event")
    if event == "action":
        return {"status": "ignored"}

    payload = await request.json()

    parsed_request = parse_github_event(event, payload)

    agent_response = orchestrator.run(parsed_request)

    if agent_response.actions:
        token = get_installation_token()
        github_client = GitHubClient(token, parsed_request)
        execute_actions(agent_response.actions, github_client)

    return {"message": "okay"}
