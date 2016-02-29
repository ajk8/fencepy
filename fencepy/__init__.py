"""
fencepy

Create a virtual environment tied to a particular directory and shortcuts to its activation.
Includes special processing if the directory is part of a git repository.  Also includes convenience
configuration for users of sublime text
"""

from ._version import __version__, __version_info__  # flake8: noqa
from .main import fence  # flake8: noqa
