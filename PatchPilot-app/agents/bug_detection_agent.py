from openai import OpenAI
from typing import List

from utils.config_utils import ConfigUtils
from utils.prompts import PromptUtils

from service.github_diff import GithubDiff
from service.github_auth import get_installation_token

class BugDetectionAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=ConfigUtils.get("OPEN_API_KEY")
        )
        self.model = ConfigUtils.get("OPEN_API_MODEL")
        # Limits
        self.max_chars_per_chunk = 4000
        self.max_chunks = 3

    def _call_llm(self, prompt):
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": PromptUtils.bug_detection_sys()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return resp.choices[0].message.content

    @staticmethod
    def _extract_diff(self, request):
        token = get_installation_token()

        diff_service = GithubDiff(
            token=token,
            owner=request.repo_owner,
            repo=request.repo_name
        )

        raw_diff = diff_service.fetch_pr_diff(request.pr_number)

        file_diffs = diff_service.split_diff_by_file(raw_diff)
        filtered = diff_service.filter_files(file_diffs)

        chunks = diff_service.select_relevant_chunks(filtered)

        return chunks

    @staticmethod
    def _build_prompt(self, diff_chunk: str) -> str:
        return PromptUtils.bug_detection_prompt(diff_chunk)

    @staticmethod
    def _aggregate_responses(self, responses: List[str]) -> str:
        return "\n\n---\n\n".join(responses)

    def run(self, request) -> str:
        chunks = self._extract_diff(request)

        if not chunks:
            return "No relevant code changes to analyze."

        responses = []

        for chunk in chunks:
            prompt = self._build_prompt(chunk)
            response = self._call_llm(prompt)
            responses.append(response)

        return self._aggregate_responses(responses)

