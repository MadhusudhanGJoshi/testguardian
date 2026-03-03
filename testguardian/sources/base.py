from abc import ABC, abstractmethod


class TestSource(ABC):
    """
    Abstract base class for all test sources.
    """

    @abstractmethod
    def scan(self):
        """
        Returns list of test metadata dictionaries.
        """
        pass
