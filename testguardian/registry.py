"""
registry.py
-----------
Unified registry for all pluggable components in TestGuardian.

Registries:
    SOURCE_REGISTRY    — test source types (filesystem, git, etc.)
    BUGSYSTEM_REGISTRY — bug system integrations (none, jira, bugzilla, etc.)

To add a new source or bug system:
    1. Create the implementation file in sources/ or bugsystems/
    2. Import it here and add it to the appropriate registry
    3. Update config.yaml with the new type string
"""

from testguardian.sources.filesystem import FileSystemSource
from testguardian.sources.git_repo import GitRepoSource
from testguardian.bugsystems.null_bugsystem import NullBugSystem

# --- Source Registry ---
SOURCE_REGISTRY = {
    "filesystem": FileSystemSource,
    "git":        GitRepoSource,
    # Future sources:
    # "s3":       S3Source,
}

# --- Bug System Registry ---
BUGSYSTEM_REGISTRY = {
    "none":     NullBugSystem,
    # Future integrations:
    # "jira":     JiraBugSystem,
    # "bugzilla": BugzillaBugSystem,
    # "github":   GitHubBugSystem,
}


def get_source(source_type, **kwargs):
    """Returns an instantiated test source for the given type."""
    if source_type not in SOURCE_REGISTRY:
        raise ValueError(
            f"Unknown source type: '{source_type}'. "
            f"Available: {list(SOURCE_REGISTRY.keys())}"
        )
    return SOURCE_REGISTRY[source_type](**kwargs)


def get_bugsystem(bugsystem_type, **kwargs):
    """Returns an instantiated bug system for the given type.
    Falls back to NullBugSystem if the type is not registered."""
    cls = BUGSYSTEM_REGISTRY.get(bugsystem_type)
    if cls is None:
        print(f"[WARNING] Unknown bug system type '{bugsystem_type}'. Falling back to NullBugSystem.")
        cls = NullBugSystem
    return cls(**kwargs)
