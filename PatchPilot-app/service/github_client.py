import requests

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
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/issues/{self.pr_number}/comments"

        res = requests.post(url, headers=self._headers(), json={"body": body})

        if res.status_code not in [200, 201]:
            raise Exception(res.text)
