"""Container version detection."""
from .base import Version
from .git import GitDetector
from .script import ScriptDetector

__all__ = [
    'Version',
    'get_all_versions',
    'get_best_version',
    'latest',
]

latest = Version('latest', False)

detectors = [
    GitDetector,
    ScriptDetector,
]


def get_all_versions(container):
    """Return a generator containing all container versions from all detectors."""
    for detector in detectors:
        for version in detector(container):
            yield version


def get_best_version(container, verify):
    """
    Return the best version for a container. If ``verify`` is ``True`` then only verified versions
    will be considered. Return ``None`` if no versions are available.
    """
    try:
        return max(get_all_versions(container))
    except ValueError:
        return None
