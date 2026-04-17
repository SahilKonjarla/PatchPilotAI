
import logging

logger = logging.getLogger(__name__)


def execute_actions(actions, github_client, request):
    for index, action in enumerate(actions, start=1):
        logger.info("Executing action %s/%s type=%s", index, len(actions), action.type)

        if action.type == "comment":
            github_client.post_comment(action.content)

        elif action.type == "commit_comment":
            github_client.post_commit_comment(
                request.commit_id,
                action.content
            )

        else:
            logger.warning("Skipping unsupported action type=%s", action.type)
