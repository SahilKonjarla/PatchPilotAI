from fastapi import Request, HTTPException
import hmac
import hashlib

from utils.config_utils import ConfigUtils
from utils.payload_parser import parse_github_event
from agents.orchestrator_agent import Orchestrator
from service.github_auth import get_installation_token
from service.github_client import GitHubClient
from service.executor import execute_actions

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
    print(f"[WEBHOOK] Event: {event}")

    payload = await request.json()
    print(f"[WEBHOOK] Keys: {list(payload.keys())}")


    parsed_request = parse_github_event(event, payload)
    print(f"[WEBHOOK] Parsed: repo={parsed_request.repo_name}, pr={parsed_request.pr_number}")
    print("[WEBHOOK] Commit ID:", parsed_request.commit_id)
    print("[WEBHOOK] Installation ID:", parsed_request.installation_id)

    agent_response = orchestrator.run(parsed_request)
    print(f"[WEBHOOK] Actions: {len(agent_response.actions)}")

    if agent_response.actions:
        token = get_installation_token(parsed_request.installation_id)
        github_client = GitHubClient(token, parsed_request)
        execute_actions(agent_response.actions, github_client, parsed_request)

    return {"message": "okay"}
