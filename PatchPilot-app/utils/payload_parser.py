import logging

from models.github_request import GitHubEventRequest

logger = logging.getLogger(__name__)


def parse_github_event(event: str, payload: dict) -> GitHubEventRequest:
    repo = payload.get("repository", {})
    repo_owner = repo.get("owner", {}).get("login")
    repo_name = repo.get("name")
    sender = payload.get("sender", {}).get("login")
    installation_id = payload.get("installation", {}).get("id")

    if not event:
        raise ValueError("Missing GitHub event type")

    if not repo_owner or not repo_name:
        raise ValueError("GitHub payload is missing repository owner or name")

    base = {
        "event_type": event,
        "repo_name": repo_name,
        "repo_owner": repo_owner,
        "sender": sender,
        "installation_id": installation_id,
        "raw_payload": payload
    }

    if event == "push":
        head_commit = payload.get("head_commit") or {}
        base.update({
            "branch": payload.get("ref", "").split("/")[-1],
            "commit_id": head_commit.get("id")
        })

    elif event == "pull_request":
        pr = payload.get("pull_request")
        if not pr:
            raise ValueError("Pull request event is missing pull_request payload")

        base.update({
            "action": payload.get("action"),
            "pr_number": pr.get("number"),
            "pr_title": pr.get("title"),
            "pr_body": pr.get("body")
        })

    elif event == "issue_comment":
        issue = payload.get("issue") or {}
        comment = payload.get("comment") or {}
        base.update({
            "action": payload.get("action"),
            "pr_number": issue.get("number"),
            "comment_body": comment.get("body")
        })

    else:
        logger.info("Parsed unsupported GitHub event into generic request: %s", event)

    try:
        return GitHubEventRequest(**base)
    except Exception as exc:
        raise ValueError(f"Invalid GitHub {event} payload: {exc}") from exc
