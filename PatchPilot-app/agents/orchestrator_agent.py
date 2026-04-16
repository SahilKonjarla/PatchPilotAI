from models.github_response import AgentResponse, AgentAction
from models.github_request import GitHubEventRequest

from agents.diff_analysis_agent import DiffAnalysisAgent
from agents.bug_detection_agent import BugDetectionAgent
from agents.code_review_agent import CodeReviewAgent
from agents.documentation_agent import DocumentationAgent
from agents.pr_summary_agent import PRSummaryAgent


class Orchestrator:
    def __init__(self):
        # Initialize all agents
        self.diff_analysis_agent = DiffAnalysisAgent()
        self.bug_agent = BugDetectionAgent()
        self.code_review_agent = CodeReviewAgent()
        self.documentation_agent = DocumentationAgent()
        self.pr_summary_agent = PRSummaryAgent()


    def run(self, request: GitHubEventRequest) -> AgentResponse:
        print(f"[ORCH] Received event: {request.event_type}")

        self._should_act(request)
        print(f"[ORCH] Should act: {should_act}")
        if not self._should_act(request):
            return self._empty_response("No action taken")

        workflow = self._select_workflow(request)
        print(f"[ORCH] Workflow: {workflow}")

        return self._execute_workflow(workflow, request)

    def _should_act(self, request: GitHubEventRequest) -> bool:
        if request.event_type == "issue_comment":
            return request.comment_body and request.comment_body.startswith("/")

        if request.event_type == "pull_request":
            return request.action in ["opened", "synchronize"]

        return False

    def _select_workflow(self, request: GitHubEventRequest) -> str:
        if request.event_type == "issue_comment":
            comment = request.comment_body.lower()

            if "/review" in comment:
                return "full_review"

            if "/summary" in comment:
                return "summary"

            if "/bugs" in comment:
                return "bugs"

            if "/document" in comment:
                return "documentation"

        if request.event_type == "pull_request":
            return "full_review"

        return "noop"


    def _execute_workflow(self, workflow: str, request: GitHubEventRequest) -> AgentResponse:
        if workflow == "full_review":
            return self._run_full_review_pipeline(request)

        if workflow == "summary":
            return self._run_summary(request)

        if workflow == "bugs":
            return self._run_bug_detection(request)

        if workflow == "documentation":
            return self._run_documentation(request)

        return self._empty_response("No matching workflow")


    def _run_full_review_pipeline(self, request: GitHubEventRequest) -> AgentResponse:
        print("[ORCH] Running full review pipeline")

        summary = self.pr_summary_agent.run(request)
        print("[AGENT] PR Summary done")

        analysis = self.diff_analysis_agent.run(request)
        print("[AGENT] Diff Analysis done")

        bugs = self.bug_agent.run(request)
        print("[AGENT] Bug Detection done")

        review = self.code_review_agent.run(request)
        print("[AGENT] Code Review done")

        combined_output = f"""
        ### PR Summary
        {summary}
        
        ---
        
        ### Diff Analysis
        {analysis}
        
        ---
        
        ### Bug Detection
        {bugs}
        
        ---
        
        ### Code Review
        {review}
        """

        return AgentResponse(
            success=True,
            message="Full PR review completed",
            agent_used="full_review_pipeline",
            actions=[
                AgentAction(
                    type="comment",
                    content=combined_output.strip()
                )
            ]
        )

    def _run_summary(self, request: GitHubEventRequest) -> AgentResponse:
        summary = self.pr_summary_agent.run(request)

        return AgentResponse(
            success=True,
            message="PR summary generated",
            agent_used="pr_summary_agent",
            actions=[
                AgentAction(
                    type="comment",
                    content=summary
                )
            ]
        )

    def _run_bug_detection(self, request: GitHubEventRequest) -> AgentResponse:
        bugs = self.bug_agent.run(request)

        return AgentResponse(
            success=True,
            message="Bug detection completed",
            agent_used="bug_detection_agent",
            actions=[
                AgentAction(
                    type="comment",
                    content=bugs
                )
            ]
        )

    def _run_documentation(self, request: GitHubEventRequest) -> AgentResponse:
        docs = self.documentation_agent.run(request)

        return AgentResponse(
            success=True,
            message="Documentation generated",
            agent_used="documentation_agent",
            actions=[
                AgentAction(
                    type="comment",
                    content=docs
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