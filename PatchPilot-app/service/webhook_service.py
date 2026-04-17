import hashlib
import hmac
import logging

from fastapi import HTTPException, Request

from agents.orchestrator_agent import Orchestrator
from service.executor import execute_actions
from service.github_auth import get_installation_token
from service.github_client import GitHubClient
from utils.config_utils import ConfigUtils
from utils.payload_parser import parse_github_event

logger = logging.getLogger(__name__)

orchestrator = Orchestrator()
config = ConfigUtils()


def _verify_signature(payload: bytes, signature: str | None) -> bool:
    if not signature:
        logger.warning("Rejected webhook with missing X-Hub-Signature-256")
        return False

    mac = hmac.new(config.get("GITHUB_WEBHOOK_SECRET").encode(), payload, hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)


async def github_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not _verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = request.headers.get("X-GitHub-Event")
    if not event:
        logger.warning("Rejected webhook with missing X-GitHub-Event")
        raise HTTPException(status_code=400, detail="Missing X-GitHub-Event header")

    try:
        payload = await request.json()
    except Exception as exc:
        logger.exception("Failed to parse GitHub webhook JSON payload")
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    logger.info("Processing GitHub event=%s payload_keys=%s", event, list(payload.keys()))

    try:
        parsed_request = parse_github_event(event, payload)
    except ValueError as exc:
        logger.warning("Unsupported or invalid GitHub event payload: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    logger.info(
        "Parsed GitHub event repo=%s/%s pr=%s commit=%s installation_id=%s",
        parsed_request.repo_owner,
        parsed_request.repo_name,
        parsed_request.pr_number,
        parsed_request.commit_id,
        parsed_request.installation_id,
    )

    try:
        agent_response = orchestrator.run(parsed_request)
    except Exception as exc:
        logger.exception("Orchestrator failed for event=%s", event)
        raise HTTPException(status_code=500, detail="Failed to process webhook") from exc

    logger.info("Orchestrator completed with %s action(s)", len(agent_response.actions))

    if agent_response.actions:
        try:
            token = get_installation_token(parsed_request.installation_id)
            github_client = GitHubClient(token, parsed_request)
            execute_actions(agent_response.actions, github_client, parsed_request)
        except Exception as exc:
            logger.exception("Failed to execute GitHub actions")
            raise HTTPException(status_code=502, detail="Failed to execute GitHub actions") from exc

    return {
        "message": "okay",
        "event": parsed_request.event_type,
        "actions": len(agent_response.actions),
    }
