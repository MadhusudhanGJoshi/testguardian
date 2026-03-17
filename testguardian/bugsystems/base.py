from abc import ABC, abstractmethod


class BugSystemBase(ABC):
    """
    Abstract base class for all bug system integrations.

    Any concrete implementation must implement get_open_bugs(),
    which returns a list of open bug identifiers linked to a given test name.

    If no bugs are found, return an empty list.
    If the bug system is unavailable, raise an exception or return [].
    """

    @abstractmethod
    def get_open_bugs(self, test_name: str) -> list:
        """
        Query the bug system for open bugs linked to the given test name.

        Parameters:
            test_name : str — the test filename (e.g. "test_login.py")

        Returns:
            list of bug identifiers (e.g. ["BUG-101", "BUG-202"])
            Empty list if no open bugs found.
        """
        pass
