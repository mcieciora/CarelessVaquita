from os import environ
from sys import argv
from argparse import ArgumentParser
from github import Auth, Github
from github.GithubException import UnknownObjectException

print("test")

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
        print(f"Created pull request: #{return_value.number}")

    def merge_pull_request(self):
        """
        Get all active pull requests with PyGitHub library.

        :return: None
        """
        active_pulls = self.github.get_user(self.username).get_repo(self.repository).get_pulls()
        if not list(active_pulls):
            print("No active pull requests.")
        for pull_request in active_pulls:
            if pull_request.mergeable and pull_request.mergeable_state == "clean":
                try:
                    pull_request.merge(delete_branch=True)
                    print(f"#{pull_request} merged successfully.")
                    break
                except UnknownObjectException:
                    active_pulls = self.github.get_user(self.username).get_repo(self.repository).get_pulls()
                    if pull_request in active_pulls:
                        print(f"#{pull_request} could not be merged automatically. Proceeding with next pull request.")
                        continue
                    print(f"#{pull_request} merged successfully, "
                          f"but experienced difficulties with branch deletion.")
                    break
            print(f"Pull request #{pull_request.number} status is {pull_request.mergeable_state}.")

    @staticmethod
    def _update_reviewers(pull_request):
        with open("required_reviewers", mode="r", encoding="utf-8") as reviewers_file:
            reviewers = reviewers_file.readlines()
            pull_request.create_review_request(reviewers)


if __name__ == "__main__":
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
