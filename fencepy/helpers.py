"""
fencepy.helpers

Shared/generic functions
"""

import os
import fnmatch
import platform
import subprocess
import sys
from contextlib import contextmanager


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


def getoutputoserror(cmd):
    """Similar behavior to commands.getstatusoutput for python 3 and windows support"""
    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.wait()
    output = p.communicate()[0].decode()
    if p.returncode:
        raise OSError(p.returncode, '{0}: {1}'.format(cmd, output))
    return output


def getpybindir():
    """Get the appropriate subdirectory for binaries depending on system"""
    if platform.system() == 'Windows':
        return 'Scripts'
    return 'bin'


def findpybin(name, start):
    """For windows compatibility"""

    # normalize to the root of the environment
    rootpath = os.path.dirname(start) if os.path.isfile(start) else start
    if os.path.basename(rootpath) in ('bin', 'Scripts'):
        rootpath = os.path.dirname(rootpath)

    # special case for Ubuntu (and other?) packaged python instances
    if rootpath == '/usr':
        binpath = os.path.join('/usr/local/bin', name)
        if os.path.exists(binpath):
            return binpath

    # we're in a linux-based virtual environment
    if 'bin' in os.listdir(rootpath):
        binpath = os.path.join(rootpath, 'bin', name)
        if os.path.exists(binpath):
            return binpath

    # we're in a windows virtual environment
    elif 'Scripts' in os.listdir(rootpath):
        binpath = os.path.join(rootpath, 'Scripts', '{0}.exe'.format(name))
        if os.path.exists(binpath):
            return binpath

    raise IOError('could not find {0} relative to {1}'.format(name, start))


@contextmanager
def redirected(out=sys.stdout, err=sys.stderr):
    saved = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = out, err
    try:
        yield
    finally:
        sys.stdout, sys.stderr = saved
