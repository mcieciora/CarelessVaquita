from os import environ
from sys import argv, exit
from argparse import ArgumentParser
from logging import basicConfig, info, INFO, warning
from collections import Counter
from github import Auth, Github
from github.GithubException import UnknownObjectException


class MergeCandidate:
    """GitHub object merge candidate class."""
    def __init__(self, pull_request, files, changes_total):
        self.pull_request = pull_request
        self.files = files
        self.changes_total = changes_total


class MergeBot:
    """Merge Bot class."""

    def __init__(self):
        self.github = Github(auth=Auth.Token(environ["GITHUB_API_TOKEN"]))
        self.username = environ["GITHUB_REPO_OWNER"]
        self.repository = environ["GITHUB_REPO_NAME"]
        self.bot_name = environ["GITHUB_BOT"]
        self.candidates = []

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

    @staticmethod
    def _update_reviewers(pull_request):
        with open("required_reviewers", mode="r", encoding="utf-8") as reviewers_file:
            reviewers = reviewers_file.readlines()
            pull_request.create_review_request(reviewers)

    def merge_pull_requests(self):
        files_counter = self.filter_pull_requests()
        if not list(self.candidates):
            info("No active pull requests.")
            exit(100)

        conflicted_pull_requests = []
        for merge_candidate in self.candidates:
            for file in merge_candidate.files:
                if files_counter[file] > 1:
                    conflicted_pull_requests.append(merge_candidate)
                    break
                else:
                    self._merge(merge_candidate.pull_request)
        lowest_changes_total = min(conflicted_pull_requests, key=lambda pr: pr.changes_total)
        self._merge(lowest_changes_total.pull_request)

    def _merge(self, pull_request):
        try:
            pull_request.merge()
            info("#%s merged successfully.", pull_request)
        except UnknownObjectException:
            active_pulls = self.github.get_user(self.username).get_repo(self.repository).get_pulls()
            if pull_request in active_pulls:
                warning("#%s could not be merged automatically.", pull_request)
            info("#%s merged successfully, "
                 "but experienced difficulties with branch deletion.", pull_request)
            exit(110)

    def filter_pull_requests(self):
        """
        Filter active pull requests list to find ones ready to merge.

        :return: List of PullRequest objects.
        """
        active_pulls = self.github.get_user(self.username).get_repo(self.repository).get_pulls()
        all_files = []
        for pull_request in active_pulls:
            # if pull_request.head.ref.startswith("test_"):
            #     info("Omitting %s in merge queue.", pull_request.head.ref)
            #     continue
            if pull_request.mergeable and pull_request.mergeable_state == "clean":
                info("#%s was accepted by the filter.", pull_request.number)
                files_info = {file.filename: file.changes for file in pull_request.get_files()}
                all_files = all_files + list(files_info.keys())
                self.candidates.append(
                    MergeCandidate(pull_request, list(files_info.keys()), sum(list(files_info.values())))
                )
            else:
                info("#%s was rejected by the filter.", pull_request.number)
        return Counter(all_files)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(".credentials")

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
        merge_bot_api.merge_pull_requests()
