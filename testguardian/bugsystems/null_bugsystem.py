from .base import BugSystemBase


class NullBugSystem(BugSystemBase):
    """
    Default no-op bug system used when no bug system is configured.

    Always returns an empty list — the agent proceeds as if
    there are no open bugs against any test.
    """

    def get_open_bugs(self, test_name: str) -> list:
        return []
