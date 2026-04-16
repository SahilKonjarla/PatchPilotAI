
def execute_actions(actions, github_client, request):
    for action in actions:
        if action.type == "comment":
            github_client.post_comment(action.content)

        elif action.type == "commit_comment":
            github_client.post_commit_comment(
                request.commit_id,
                action.content
            )