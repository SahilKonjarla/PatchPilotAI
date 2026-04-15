from typing import List, Optional
from pydantic import BaseModel

class AgentAction(BaseModel):
    type: str  # "comment", "commit", "none"
    content: Optional[str] = None
    file_path: Optional[str] = None
    commit_message: Optional[str] = None


class AgentResponse(BaseModel):
    success: bool
    message: str

    actions: List[AgentAction] = []

    # metadata for logging/debugging
    agent_used: Optional[str] = None
