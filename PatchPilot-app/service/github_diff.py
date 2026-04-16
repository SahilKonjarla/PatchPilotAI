import requests

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
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls/{pr_number}"

        response = requests.get(url, headers=self.headers())

        if response.status_code != 200:
            raise Exception(f"Failed to fetch PR diff: {response.text}")

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
                continue

            if "node_modules" in first_line:
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

        return selected

    def fetch_commit_diff(self, commit_sha):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/commits/{commit_sha}"

        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3.diff"
        }

        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            raise Exception(res.text)

        return res.text
