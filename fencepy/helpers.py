"""
fencepy.helpers

Shared/generic functions
"""

import os
import fnmatch


def pseudo_merge_dict(dto, dfrom):
    """Recursively merge dict objects, overwriting any non-dict values"""

    # a quick type check
    if not (type(dto) == dict and type(dfrom) == dict):
        raise ValueError('non-dict passed into _psuedo_merge_dict')

    # do the work
    for k, v in dfrom.items():
        if k not in dto.keys():
            dto[k] = v

        # recurse on further dicts
        elif type(dfrom[k]) == dict:
            pseudo_merge_dict(dto[k], dfrom[k])

        # everything else can just be overwritten
        else:
            dto[k] = dfrom[k]


def locate_subdirs(pattern, root):
    """Get a list of all subdirectories contained underneath a root"""

    ret = []
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for subdir in fnmatch.filter(dirs, pattern):
            ret.append(os.path.join(path, subdir))
    return ret
