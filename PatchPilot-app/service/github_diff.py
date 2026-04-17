import logging

import requests

logger = logging.getLogger(__name__)


class GithubDiff:
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo

    def headers(self):
        return {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3.diff'
        }

    def fetch_pr_diff(self, pr_number: int) -> str:
        if not pr_number:
            raise ValueError("pr_number is required to fetch a pull request diff")

        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls/{pr_number}"

        logger.info("Fetching PR diff repo=%s/%s pr=%s", self.owner, self.repo, pr_number)
        try:
            response = requests.get(url, headers=self.headers(), timeout=20)
        except requests.RequestException as exc:
            logger.exception("Failed to fetch PR diff")
            raise RuntimeError("Failed to fetch PR diff") from exc

        if response.status_code != 200:
            logger.error("Failed to fetch PR diff status=%s body=%s", response.status_code, response.text)
            raise RuntimeError(f"Failed to fetch PR diff: {response.status_code}")

        return response.text

    def filter_files(self, file_diffs):
        ignored_extensions = [
            ".lock", ".png", ".jpg", ".jpeg", ".gif",
            ".svg", ".ico", ".pdf"
        ]

        filtered = []

        for file_diff in file_diffs:
            first_line = file_diff.split("\n")[0]

            if any(ext in first_line for ext in ignored_extensions):
                logger.debug("Skipping ignored file diff: %s", first_line)
                continue

            if "node_modules" in first_line:
                logger.debug("Skipping node_modules file diff: %s", first_line)
                continue

            filtered.append(file_diff)

        return filtered

    def split_diff_by_file(self, diff_text: str):
        files = diff_text.split("diff --git")
        parsed_files = []

        for file_chunk in files:
            if not file_chunk.strip():
                continue

            parsed_files.append("diff --git " + file_chunk)

        return parsed_files

    def select_relevant_chunks(self, file_diffs, max_chunks=3, max_chars=4000):
        selected = []

        for file_diff in file_diffs[:max_chunks]:
            selected.append(file_diff[:max_chars])

        logger.info("Selected %s diff chunk(s) for analysis", len(selected))
        return selected

    def fetch_commit_diff(self, commit_sha):
        if not commit_sha:
            raise ValueError("commit_sha is required to fetch a commit diff")

        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/commits/{commit_sha}"

        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3.diff"
        }

        logger.info("Fetching commit diff repo=%s/%s commit=%s", self.owner, self.repo, commit_sha)
        try:
            res = requests.get(url, headers=headers, timeout=20)
        except requests.RequestException as exc:
            logger.exception("Failed to fetch commit diff")
            raise RuntimeError("Failed to fetch commit diff") from exc

        if res.status_code != 200:
            logger.error("Failed to fetch commit diff status=%s body=%s", res.status_code, res.text)
            raise RuntimeError(f"Failed to fetch commit diff: {res.status_code}")

        return res.text
