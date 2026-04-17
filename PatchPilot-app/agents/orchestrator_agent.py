import logging
from typing import Callable, Optional

from agents.bug_detection_agent import BugDetectionAgent
from agents.code_review_agent import CodeReviewAgent
from agents.diff_analysis_agent import DiffAnalysisAgent
from agents.documentation_agent import DocumentationAgent
from agents.pr_summary_agent import PRSummaryAgent
from agents.security_agent import SecurityAgent
from agents.test_coverage_agent import TestCoverageAgent
from models.github_request import GitHubEventRequest
from models.github_response import AgentAction, AgentResponse

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self):
        self.diff_analysis_agent = DiffAnalysisAgent()
        self.bug_agent = BugDetectionAgent()
        self.code_review_agent = CodeReviewAgent()
        self.documentation_agent = DocumentationAgent()
        self.pr_summary_agent = PRSummaryAgent()
        self.security_agent = SecurityAgent()
        self.test_coverage_agent = TestCoverageAgent()

    def run(self, request: GitHubEventRequest) -> AgentResponse:
        logger.info("Received event_type=%s action=%s", request.event_type, request.action)

        should_act = self._should_act(request)
        logger.info("Should act on event_type=%s: %s", request.event_type, should_act)
        if not should_act:
            return self._empty_response("No action taken")

        workflow = self._select_workflow(request)
        logger.info("Selected workflow=%s", workflow)

        return self._execute_workflow(workflow, request)

    def _should_act(self, request: GitHubEventRequest) -> bool:
        if request.event_type == "push":
            return bool(request.commit_id)

        if request.event_type == "issue_comment":
            return bool(request.comment_body and request.comment_body.startswith("/"))

        if request.event_type == "pull_request":
            return request.action in ["opened", "reopened", "ready_for_review", "synchronize"]

        return False

    def _select_workflow(self, request: GitHubEventRequest) -> str:
        if request.event_type == "push":
            return "push_analysis"

        if request.event_type == "issue_comment":
            comment = (request.comment_body or "").lower()

            if "/review" in comment or "/full" in comment:
                return "full_review"

            if "/summary" in comment:
                return "summary"

            if "/bugs" in comment:
                return "bugs"

            if "/security" in comment:
                return "security"

            if "/tests" in comment or "/coverage" in comment:
                return "test_coverage"

            if "/quality" in comment:
                return "code_quality"

            if "/diff" in comment:
                return "diff_analysis"

            if "/document" in comment or "/docs" in comment:
                return "documentation"

        if request.event_type == "pull_request":
            return "full_review"

        return "noop"

    def _execute_workflow(self, workflow: str, request: GitHubEventRequest) -> AgentResponse:
        workflows = {
            "full_review": self._run_full_review_pipeline,
            "push_analysis": self._run_push_analysis,
            "summary": self._run_summary,
            "bugs": self._run_bug_detection,
            "security": self._run_security,
            "test_coverage": self._run_test_coverage,
            "code_quality": self._run_code_quality,
            "diff_analysis": self._run_diff_analysis,
            "documentation": self._run_documentation,
        }

        handler = workflows.get(workflow)
        if not handler:
            return self._empty_response("No matching workflow")

        return handler(request)

    def _run_full_review_pipeline(self, request: GitHubEventRequest) -> AgentResponse:
        logger.info("Running full review pipeline")

        sections = [
            ("PR Summary", self._run_agent("pr_summary_agent", self.pr_summary_agent.run, request)),
            ("Diff Analysis", self._run_agent("diff_analysis_agent", self.diff_analysis_agent.run, request)),
            ("Bug Detection", self._run_agent("bug_detection_agent", self.bug_agent.run, request)),
            ("Security Review", self._run_agent("security_agent", self.security_agent.run, request)),
            ("Test Coverage", self._run_agent("test_coverage_agent", self.test_coverage_agent.run, request)),
            ("Code Quality", self._run_agent("code_review_agent", self.code_review_agent.run, request)),
            ("Documentation", self._run_agent("documentation_agent", self.documentation_agent.run, request)),
        ]

        return AgentResponse(
            success=True,
            message="Full PR review completed",
            agent_used="full_review_pipeline",
            actions=[
                AgentAction(
                    type="comment",
                    content=self._format_sections(sections)
                )
            ]
        )

    def _run_push_analysis(self, request: GitHubEventRequest) -> AgentResponse:
        logger.info(
            "Running expanded push analysis repo=%s/%s branch=%s commit=%s",
            request.repo_owner,
            request.repo_name,
            request.branch,
            request.commit_id,
        )

        sections = [
            ("Commit Summary", self._run_agent("pr_summary_agent", self.pr_summary_agent.run, request)),
            ("Changed Files and Impact", self._run_agent("diff_analysis_agent", self.diff_analysis_agent.run, request)),
            ("Bug Risks", self._run_agent("bug_detection_agent", self.bug_agent.run, request)),
            ("Security Risks", self._run_agent("security_agent", self.security_agent.run, request)),
            ("Test Coverage Gaps", self._run_agent("test_coverage_agent", self.test_coverage_agent.run, request)),
            ("Code Quality Notes", self._run_agent("code_review_agent", self.code_review_agent.run, request)),
        ]

        content = f"""
        ## PatchPilot Push Review

        Repository: `{request.repo_owner}/{request.repo_name}`
        Branch: `{request.branch}`
        Commit: `{request.commit_id}`

        {self._format_sections(sections)}
        """.strip()

        return AgentResponse(
            success=True,
            message="Push analyzed",
            agent_used="push_pipeline",
            actions=[
                AgentAction(
                    type="commit_comment",
                    content=content
                )
            ]
        )

    def _run_summary(self, request: GitHubEventRequest) -> AgentResponse:
        summary = self._run_agent("pr_summary_agent", self.pr_summary_agent.run, request)
        return self._comment_response("PR summary generated", "pr_summary_agent", summary)

    def _run_bug_detection(self, request: GitHubEventRequest) -> AgentResponse:
        bugs = self._run_agent("bug_detection_agent", self.bug_agent.run, request)
        return self._comment_response("Bug detection completed", "bug_detection_agent", bugs)

    def _run_security(self, request: GitHubEventRequest) -> AgentResponse:
        security = self._run_agent("security_agent", self.security_agent.run, request)
        return self._comment_response("Security review completed", "security_agent", security)

    def _run_test_coverage(self, request: GitHubEventRequest) -> AgentResponse:
        tests = self._run_agent("test_coverage_agent", self.test_coverage_agent.run, request)
        return self._comment_response("Test coverage review completed", "test_coverage_agent", tests)

    def _run_code_quality(self, request: GitHubEventRequest) -> AgentResponse:
        review = self._run_agent("code_review_agent", self.code_review_agent.run, request)
        return self._comment_response("Code quality review completed", "code_review_agent", review)

    def _run_diff_analysis(self, request: GitHubEventRequest) -> AgentResponse:
        analysis = self._run_agent("diff_analysis_agent", self.diff_analysis_agent.run, request)
        return self._comment_response("Diff analysis completed", "diff_analysis_agent", analysis)

    def _run_documentation(self, request: GitHubEventRequest) -> AgentResponse:
        docs = self._run_agent("documentation_agent", self.documentation_agent.run, request)
        return self._comment_response("Documentation review completed", "documentation_agent", docs)

    def _run_agent(
        self,
        agent_name: str,
        runner: Callable[[GitHubEventRequest], str],
        request: GitHubEventRequest,
    ) -> str:
        try:
            result = runner(request)
            logger.info("Agent completed agent=%s", agent_name)
            return result
        except Exception as exc:
            logger.exception("Agent failed agent=%s", agent_name)
            return f"{agent_name} failed: {exc}"

    def _format_sections(self, sections: list[tuple[str, str]]) -> str:
        return "\n\n---\n\n".join(
            f"### {title}\n{content.strip() if content else 'No output generated.'}"
            for title, content in sections
        )

    def _comment_response(self, message: str, agent_used: str, content: Optional[str]) -> AgentResponse:
        return AgentResponse(
            success=True,
            message=message,
            agent_used=agent_used,
            actions=[
                AgentAction(
                    type="comment",
                    content=content or "No output generated."
                )
            ]
        )

    def _empty_response(self, message: str) -> AgentResponse:
        return AgentResponse(
            success=True,
            message=message,
            actions=[],
            agent_used=None
        )
