from models.github_request import GitHubEventRequest

def parse_github_event(event: str, payload: dict) -> GitHubEventRequest:
    repo = payload.get("repository", {})

    base = {
        "event_type": event,
        "repo_name": repo.get("name"),
        "repo_owner": repo.get("owner", {}).get("login"),
        "sender": payload.get("sender", {}).get("login"),
        "installation_id": payload.get("installation", {}).get("id"),  # <-- ADD THIS
        "raw_payload": payload
    }

    if event == "push":
        base.update({
            "branch": payload.get("ref", "").split("/")[-1],
            "commit_id": payload.get("head_commit", {}).get("id")
        })

    elif event == "pull_request":
        pr = payload["pull_request"]
        base.update({
            "action": payload["action"],
            "pr_number": pr["number"],
            "pr_title": pr["title"],
            "pr_body": pr["body"]
        })

    elif event == "issue_comment":
        base.update({
            "action": payload["action"],
            "pr_number": payload["issue"]["number"],
            "comment_body": payload["comment"]["body"]
        })

    return GitHubEventRequest(**base)
