from models.github_request import GitHubEventRequest

def parse_github_event(event: str, payload: dict) -> GitHubEventRequest:
    base = {
        "event_type": event,
        "repo_name": payload["repository"]["name"],
        "repo_owner": payload["repository"]["owner"]["login"],
        "sender": payload["sender"]["login"],
        "raw_payload": payload
    }

    if event == "push":
        base.update({
            "branch": payload["ref"].split("/")[-1],
            "commit_id": payload["head_commit"]["id"]
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
