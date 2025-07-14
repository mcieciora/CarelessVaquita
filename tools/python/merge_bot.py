from os import environ
from sys import argv, exit
from argparse import ArgumentParser
from logging import basicConfig, info, INFO, warning
from github import Auth, Github
from github.GithubException import UnknownObjectException


class MergeBot:
    """Merge Bot class."""

    def __init__(self):
        self.github = Github(auth=Auth.Token(environ["GITHUB_API_TOKEN"]))
        self.username = environ["GITHUB_USER"]
        self.repository = environ["GITHUB_REPO"]
        self.bot_name = environ["GITHUB_BOT"]

    def create_pull_request(self, branch_name, base_branch):
        """
        Create pull request with PyGitHub library.

        :return: None
        """
        return_value = self.github.get_user(self.username).get_repo(self.repository).create_pull(
            base=base_branch,
            head=branch_name,
            title=f"Merge {branch_name}",
            body=f"Automatically created pull request that merges {branch_name} into {base_branch}."
        )
        self._update_reviewers(return_value)
        info("Created pull request: #%s", return_value.number)

    def merge_pull_request(self):
        """
        Get all active pull requests with PyGitHub library.

        :return: None
        """
        default_exit_code = 0
        active_pulls = self.github.get_user(self.username).get_repo(self.repository).get_pulls()
        found_mergeable_pull_request = False
        if not list(active_pulls):
            info("No active pull requests.")
            default_exit_code = 100
        for pull_request in active_pulls:
            if pull_request.mergeable and pull_request.mergeable_state == "clean":
                found_mergeable_pull_request = True
                try:
                    pull_request.merge(delete_branch=True)
                    info("#%s merged successfully.", pull_request)
                    break
                except UnknownObjectException:
                    active_pulls = self.github.get_user(self.username).get_repo(self.repository).get_pulls()
                    if pull_request in active_pulls:
                        warning("#%s could not be merged automatically. "
                                       "Proceeding with next pull request.", pull_request)
                        continue
                    info("#%s merged successfully, "
                                "but experienced difficulties with branch deletion.", pull_request)
                    default_exit_code = 110
            info("Pull request #%s status is %s.", pull_request.number, pull_request.mergeable_state)
        if not found_mergeable_pull_request:
            default_exit_code = 120
        exit(default_exit_code)

    @staticmethod
    def _update_reviewers(pull_request):
        with open("required_reviewers", mode="r", encoding="utf-8") as reviewers_file:
            reviewers = reviewers_file.readlines()
            pull_request.create_review_request(reviewers)


if __name__ == "__main__":
    basicConfig(level=INFO)
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--create", help="Create pull request. Usage: merge_bot.py --create [--branch] branch "
                                        "name\n[--base] base branch", action="store_true")
    group.add_argument("--merge", action="store_true", help="Merge branch. Usage: merge_bot.py --merge")
    if "--create" in argv:
        parser.add_argument("--branch", dest="branch_name", required=True, help="Branch name")
        parser.add_argument("--base", dest="base_branch", required=True, help="Base branch")
    args = parser.parse_args()

    merge_bot_api = MergeBot()
    if args.create:
        merge_bot_api.create_pull_request(args.branch_name, args.base_branch)
    else:
        merge_bot_api.merge_pull_request()
