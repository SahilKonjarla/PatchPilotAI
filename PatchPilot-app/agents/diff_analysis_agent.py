import logging
from typing import List

from openai import OpenAI

from service.github_auth import get_installation_token
from service.github_diff import GithubDiff
from utils.config_utils import ConfigUtils
from utils.prompts import PromptUtils

logger = logging.getLogger(__name__)
config = ConfigUtils()
prompt_utils = PromptUtils()

class DiffAnalysisAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=config.get(key="OPENAI_API_KEY")
        )
        self.model = config.get("OPENAI_MODEL")
        self.max_chunks = 3
        self.max_chars_per_chunk = 4000

    def run(self, request) -> str:
        logger.info("Running diff analysis agent")
        diff_chunks = self._extract_diff_chunks(request)

        if not diff_chunks:
            return "No relevant code changes found for review."

        responses = []
        for index, diff_chunk in enumerate(diff_chunks, start=1):
            logger.info("Analyzing diff chunk %s/%s", index, len(diff_chunks))
            prompt = self._build_prompt(diff_chunk)
            response = self._call_llm(prompt)
            responses.append(response)

        return self._aggregate_responses(responses)


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

    def _build_prompt(self, diff_chunk: str):
        return prompt_utils.diff_analysis_prompt(diff_chunk)

    def _call_llm(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": prompt_utils.diff_analysis_sys()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2
            )
        except Exception as exc:
            logger.exception("Diff analysis LLM call failed")
            raise RuntimeError("Diff analysis LLM call failed") from exc

        return (response.choices[0].message.content or "").strip()

    def _aggregate_responses(self, responses: List[str]) -> str:
        cleaned_responses = [response.strip() for response in responses if response and response.strip()]

        if not cleaned_responses:
            return "No review feedback generated."

        return "\n\n---\n\n".join(cleaned_responses)
