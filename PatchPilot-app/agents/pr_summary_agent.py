import openai
from typing import List

from service.github_auth import get_installation_token
from service.github_diff import GithubDiff
from utils.config_utils import ConfigUtils
from utils.prompts import PromptUtils

config = ConfigUtils()

class PRSummaryAgent:
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
            return "No changes found to summarize."

        # Step 1: summarize each chunk
        chunk_summaries = []
        for chunk in diff_chunks:
            prompt = PromptUtils.pr_summary_prompt(chunk)
            response = self._call_llm(prompt)
            chunk_summaries.append(response)

        # Step 2: aggregate into final PR summary
        final_prompt = PromptUtils.pr_summary_aggregate_prompt(chunk_summaries)
        final_summary = self._call_llm(final_prompt)

        return final_summary

    def _extract_diff_chunks(self, request) -> List[str]:
        if not request.pr_number:
            return []

        token = get_installation_token()

        diff_service = GithubDiff(
            token=token,
            owner=request.repo_owner,
            repo=request.repo_name
        )

        raw_diff = diff_service.fetch_pr_diff(request.pr_number)
        file_diffs = diff_service.split_diff_by_file(raw_diff)
        filtered = diff_service.filter_files(file_diffs)

        return diff_service.select_relevant_chunks(
            filtered,
            max_chunks=self.max_chunks,
            max_chars=self.max_chars_per_chunk
        )

    def _call_llm(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": PromptUtils.pr_sys()
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        return response.choices[0].message.content.strip()
