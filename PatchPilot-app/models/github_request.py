from pydantic import BaseModel
from typing import Optional, Dict, Any

class GitHubEventRequest(BaseModel):
    event_type: str
    action: Optional[str] = None

    repo_name: str
    repo_owner: str

    sender: str

    # Optional fields depending on event
    branch: Optional[str] = None
    commit_id: Optional[str] = None

    pr_number: Optional[int] = None
    pr_title: Optional[str] = None
    pr_body: Optional[str] = None

    comment_body: Optional[str] = None
    installation_id: int | None = None

    # raw payload (for flexibility/debugging)
    raw_payload: Dict[str, Any]
