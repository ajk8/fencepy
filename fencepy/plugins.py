"""
fencepy.plugins

Plugins for use during environment creation
"""

import json
import os
import platform
import sys
from .helpers import pseudo_merge_dict, locate_subdirs, getoutputoserror, findpybin, getpybindir, pyversionstr

# set up logging
import logging
l = logging.getLogger('')

PLUGINS = ['requirements', 'sublime', 'ps1']


def install_requirements(args):
    """Install requirements out of requirements.txt, if it exists"""

    # break out various args for convenience
    vdir = args['virtualenv_dir']
    pdir = args['dir']

    # install requirements, if they exist
    rtxt = os.path.join(pdir, 'requirements.txt')
    if os.path.exists(rtxt):
        l.info('loading requirements from {0}'.format(rtxt))
        try:
            output = getoutputoserror('{0} install -r {1}'.format(findpybin('pip', vdir), rtxt))
            l.debug(''.ljust(40, '='))
            l.debug(output)
            l.debug(''.ljust(40, '='))
        except OSError as e:
            l.error(str(e))
            return 1
        l.info('finished installing requirements')
        return 0


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
                'paths': {'linux': [os.path.join(vdir, getpybindir())]},
                'python_paths': {'linux': locate_subdirs('site-packages', vdir)}
            }
        }
        pseudo_merge_dict(cfg_dict, dict_data)
        json.dump(cfg_dict, open(scfg, 'w'), indent=4, separators=(', ', ': '), sort_keys=True)
        l.info('successfully configured sublime linter')

    return 0


def install_ps1(args):
    """Change the PS1 environment name in activate scripts"""

    ps1str = '-'.join((os.path.basename(args['dir']), pyversionstr()))
    vdir = args['virtualenv_dir']

    system = platform.system()
    if system == 'Linux':
        subdir = 'bin'
        mods = {
            'activate': {
                'from': '(`basename \\"$VIRTUAL_ENV\\"`)',
                'to': ps1str
            },
            'activate.csh': {
                'from': '`basename "$VIRTUAL_ENV"`',
                'to': ps1str
            },
            'activate.fish': {
                'from': '(basename "$VIRTUAL_ENV")',
                'to': ps1str
            }
        }
    elif system == 'Windows':
        subdir = 'Scripts'
        mods = {
            'activate.bat': {
                'from': '({0})'.format(os.path.basename(vdir)),
                'to': '({0})'.format(ps1str)
            },
            'activate.ps1': {
                'from': '$(split-path $env:VIRTUAL_ENV -leaf)',
                'to': ps1str
            }
        }
    else:
        l.error('unrecognized platform.system(): {0}, cannot modify ps1 text'.format(system))
        return 1

    for filename, trans in mods.items():
        filepath = os.path.join(vdir, subdir, filename)
        text = open(filepath, 'r').read()
        if trans['from'] in text:

            # workaround for issue that throws UnicodeDecodeError in windows
            if filename == 'activate.ps1' and sys.getdefaultencoding() == 'ascii':
                text = text.decode('utf-8', 'ignore')
                text = text.replace(trans['from'], trans['to'])
                text = text.encode('ascii', 'ignore')
            else:
                text = text.replace(trans['from'], trans['to'])

            open(filepath, 'w').write(text)

    return 0
