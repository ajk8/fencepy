"""
fencepy.plugins

Plugins for use during environment creation
"""

import sh
import json
import os
from .helpers import pseudo_merge_dict, locate_subdirs, QUIET, qprint as _print

# set up logging
import logging
l = logging.getLogger('')


def install_requirements(args):
    """Install requirements out of requirements.txt, if it exists"""

    # break out various args for convenience
    vdir = args['virtualenv_dir']
    pdir = args['dir']

    # install requirements, if they exist
    rtxt = os.path.join(pdir, 'requirements.txt')
    if os.path.exists(rtxt):
        l.info('loading requirements from {0}'.format(rtxt))
        _print(''.ljust(40, '='))
        output = sh.Command(os.path.join(vdir, 'bin', 'pip'))('install', '-r', rtxt, _out=_print, _err=_print)
        output.wait()
        _print(''.ljust(40, '='))
        if output.exit_code:
            return 1
        l.info('finished installing requirements')


def install_sublime(args):
    """Set up sublime linter to use environment"""

    # break out various args for convenience
    vdir = args['virtualenv_dir']
    pdir = args['dir']

    # set up the sublime linter, if appropriate
    scfg = None
    for filename in os.listdir(pdir):
        if filename.endswith('.sublime-project'):
            scfg = os.path.join(pdir, filename)
            break
    if scfg:
        l.debug('configuring sublime linter in file {0}'.format(scfg))
        cfg_dict = json.load(open(scfg))
        dict_data = {
            'SublimeLinter': {
                'paths': {'linux': [os.path.join(vdir, 'bin')]},
                'python_paths': {'linux': locate_subdirs('site-packages', vdir)}
            }
        }
        pseudo_merge_dict(cfg_dict, dict_data)
        json.dump(cfg_dict, open(scfg, 'w'), indent=4, separators=(', ', ': '), sort_keys=True)
        l.info('successfully configured sublime linter')
