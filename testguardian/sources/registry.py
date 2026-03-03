from .filesystem import FileSystemSource
from .git_repo import GitRepoSource


SOURCE_REGISTRY = {
    "filesystem": FileSystemSource,
    "git": GitRepoSource,
}


def get_source(source_type, **kwargs):
    if source_type not in SOURCE_REGISTRY:
        raise ValueError(f"Unknown source type: {source_type}")

    return SOURCE_REGISTRY[source_type](**kwargs)
