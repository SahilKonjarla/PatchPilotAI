import logging

import requests

logger = logging.getLogger(__name__)


class GitHubClient:
    def __init__(self, token, request):
        self.token = token
        self.repo = request.repo_name
        self.owner = request.repo_owner
        self.pr_number = request.pr_number

    def _headers(self):
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json"
        }

    def post_comment(self, body: str):
        if not self.pr_number:
            raise ValueError("pr_number is required to post a pull request comment")

        logger.info("Posting GitHub PR comment repo=%s/%s pr=%s", self.owner, self.repo, self.pr_number)
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/issues/{self.pr_number}/comments"

        try:
            res = requests.post(url, headers=self._headers(), json={"body": body}, timeout=20)
        except requests.RequestException as exc:
            logger.exception("Failed to post GitHub PR comment")
            raise RuntimeError("Failed to post GitHub PR comment") from exc

        if res.status_code not in [200, 201]:
            logger.error("GitHub PR comment failed status=%s body=%s", res.status_code, res.text)
            raise RuntimeError(f"GitHub PR comment failed: {res.status_code}")

        logger.info("Posted GitHub PR comment status=%s", res.status_code)

    def post_commit_comment(self, commit_sha: str, body: str):
        if not commit_sha:
            raise ValueError("commit_sha is required to post a commit comment")

        logger.info("Posting GitHub commit comment repo=%s/%s commit=%s", self.owner, self.repo, commit_sha)
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/commits/{commit_sha}/comments"

        try:
            res = requests.post(
                url,
                headers=self._headers(),
                json={"body": body},
                timeout=20,
            )
        except requests.RequestException as exc:
            logger.exception("Failed to post GitHub commit comment")
            raise RuntimeError("Failed to post GitHub commit comment") from exc

        if res.status_code not in [200, 201]:
            logger.error("GitHub commit comment failed status=%s body=%s", res.status_code, res.text)
            raise RuntimeError(f"GitHub commit comment failed: {res.status_code}")

        logger.info("Posted GitHub commit comment status=%s", res.status_code)
