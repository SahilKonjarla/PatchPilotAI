import openai
from typing import List

from service.github_auth import get_installation_token
from service.github_diff import GithubDiff
from utils.config_utils import ConfigUtils
from utils.prompts import PromptUtils

config = ConfigUtils()
prompt_utils = PromptUtils()

class DocumentationAgent:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=config.get("OPENAI_API_KEY")
        )
        self.model = config.get("OPENAI_MODEL")

        self.max_chunks = 3
        self.max_chars_per_chunk = 4000

    def run(self, request) -> str:
        diff_chunks = self._extract_diff_chunks(request)

        if not diff_chunks:
            return "No relevant code changes to document."

        responses = []
        for chunk in diff_chunks:
            prompt = self._build_prompt(chunk)
            response = self._call_llm(prompt)
            responses.append(response)

        return self._aggregate_responses(responses)\

    def _extract_diff_chunks(self, request) -> List[str]:
        token = get_installation_token(request.installation_id)

        diff_service = GithubDiff(
            token=token,
            owner=request.repo_owner,
            repo=request.repo_name
        )

        if request.pr_number:
            raw_diff = diff_service.fetch_pr_diff(request.pr_number)
        elif request.commit_id:
            raw_diff = diff_service.fetch_commit_diff(request.commit_id)
        else:
            return []

        file_diffs = diff_service.split_diff_by_file(raw_diff)
        filtered_diffs = diff_service.filter_files(file_diffs)

        return diff_service.select_relevant_chunks(
            filtered_diffs,
            max_chunks=self.max_chunks,
            max_chars=self.max_chars_per_chunk
        )

    def _build_prompt(self, diff_chunk: str) -> str:
        return prompt_utils.document_prompt(diff_chunk)

    def _call_llm(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": prompt_utils.document_sys()
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    def _aggregate_responses(self, responses: List[str]) -> str:
        cleaned = [r.strip() for r in responses if r and r.strip()]

        if not cleaned:
            return "No documentation generated."

        return "\n\n---\n\n".join(cleaned)