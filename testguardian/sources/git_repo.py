from .base import TestSource


class GitRepoSource(TestSource):
    def __init__(self, repo_url):
        self.repo_url = repo_url

    def scan(self):
        """
        Future: clone repo, analyze commit history,
        extract metadata like churn, last modified etc.
        """
        raise NotImplementedError("Git scanning not implemented yet.")
