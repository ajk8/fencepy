"""
fencepy.main

Main CLI logic
"""

import argparse
import os
import shutil
import sys
from . import plugins
from .helpers import getoutputoserror, findpybin

FENCEPY_ROOT = os.path.join(os.path.expanduser('~'), '.fencepy')
if not os.path.exists(FENCEPY_ROOT):
    os.mkdir(FENCEPY_ROOT)

import logging as l
l.basicConfig(filename=os.path.join(FENCEPY_ROOT, 'fencepy.log'))

VENV_ROOT = os.path.join(FENCEPY_ROOT, 'virtualenvs')


def _get_args():
    """Do all parsing and processing for command-line arguments"""

    parser = argparse.ArgumentParser(prog='fencepy',
                                     usage='%(prog)s -a|-c|-e [options]',
                                     add_help=False)

    # action arguments
    actions = parser.add_argument_group('actions')
    actions.add_argument('-a', '--activate', action='store_true',
                         help='Print the path to the activate script in the fenced environment -- this is the default behavior')
    actions.add_argument('-c', '--create', action='store_true',
                         help='Create the fenced environment')
    actions.add_argument('-e', '--erase', action='store_true',
                         help='Erase the fenced environment')

    # source and destination arguments
    paths = parser.add_argument_group('path overrides')
    paths.add_argument('-p', '--plain', action='store_true',
                       help="Don't treat the working directory as a git repository")
    paths.add_argument('-d', '--dir',
                       help='Use DIR as the root path for the fenced environment instead of the CWD')
    paths.add_argument('-D', '--virtualenv-dir', metavar='DIR',
                       help='Use DIR as the root directory for the virtualenv instead of the default')

    # miscellaneous functionality
    misc = parser.add_argument_group('miscellaneous')
    misc.add_argument('-P', '--plugins',
                      help='Comma-separated list of plugins to apply, defaults to all plugins')
    misc.add_argument('-v', '--verbose', '--debug', action='store_true',
                      help='Print debug logging')
    misc.add_argument('-q', '--quiet', action='store_true',
                      help='Silence all console output')
    misc.add_argument("-h", "--help", action="help",
                      help="show this help message and exit")
    args = vars(parser.parse_args())

    # set up logging
    if not args['quiet']:
        f = l.Formatter('[%(levelname)s] %(message)s')
        h = l.StreamHandler()
        h.setFormatter(f)
        l.getLogger('').addHandler(h)

    if args['verbose']:
        l.getLogger('').setLevel(l.DEBUG)
        l.getLogger('sh').setLevel(l.INFO)
    else:
        l.getLogger('').setLevel(l.INFO)
        l.getLogger('sh').setLevel(l.ERROR)

    # we need to do some work to get the root directory we care about here
    if not args['dir']:
        args['dir'] = os.getcwd()
    if not args['plain']:
        try:
            output = getoutputoserror('git rev-parse --show-toplevel')
            args['dir'] = output.strip()
        except OSError as e:
            l.debug("tried to handle {0} as a git repository but it isn't one".format(args['dir']))

    # keep track of the python version for later
    args['pyversion'] = '.'.join([str(x) for x in sys.version_info[:2]])

    # reset the virtualenv root, if necessary
    if not args['virtualenv_dir']:

        # if we're one directory below the root, this logic needs to work differently
        parent = os.path.dirname(args['dir'])
        if parent in ('/', os.path.splitdrive(parent)[0]):
            args['virtualenv_dir'] = os.path.join(VENV_ROOT, os.path.basename(args['dir']))

        else:
            # need the realpath here because in some circumstances windows paths get passed
            # with a '/' and others see it coming in as a '\'
            tokens = os.path.dirname(os.path.realpath(args['dir'])).split(os.path.sep)
            tokens.reverse()
            if tokens[-1] == '':
                tokens = tokens[:-1]
            prjpart = '.'.join([os.path.basename(args['dir']), '.'.join([d[0] for d in tokens])])
            args['virtualenv_dir'] = os.path.join(VENV_ROOT, '-'.join((prjpart, args['pyversion'])))

    # set the mode properly
    modecount = [args['activate'], args['create'], args['erase']].count(True)
    if modecount > 1:
        l.error("please specify only one of -a, -c, -e")
    elif modecount == 0:
        args['activate'] = True

    # plugins
    args['plugins'] = args['plugins'].split(',') if args['plugins'] else ['sublime', 'requirements', 'ps1']

    return args


def _activate(args):
    """Print out the path to the appropriate activate script"""

    # break out the virtual environment directory for convenience
    vdir = args['virtualenv_dir']

    # make sure the directory exists
    if not os.path.exists(vdir):
        l.error('virtual environment does not exist, create it with -c')
        return 1

    # unix-based shells
    if 'SHELL' in os.environ.keys():
        if os.environ['SHELL'].endswith('fish'):
            apath = os.path.join(vdir, 'bin', 'activate.fish')
        elif os.environ['SHELL'].endswith('csh'):
            apath = os.path.join(vdir, 'bin', 'activate.csh')
        else:
            apath = os.path.join(vdir, 'bin', 'activate')

    # windows -- get-help will always raise the OSError, but we can still use it for this
    else:
        try:
            getoutputoserror('get-help')
        except OSError as e:
            if 'not recognized' in str(e):
                apath = os.path.join(vdir, 'Scripts', 'activate.bat')
            else:
                apath = os.path.join(vdir, 'Scripts', 'activate.ps1')

    # i don't think it's possible to set the calling environment,
    # so we'll just print the path to the script
    print(apath)
    return 0


def _create(args):
    """Create a virtualenv for the current project"""

    # break out various args for convenience
    vdir = args['virtualenv_dir']
    pdir = args['dir']  # p for project

    # make sure the directory doesn't already exist
    if os.path.exists(vdir):
        l.error('virtual environment already exists, quitting')
        return 1

    # also make sure the project dir does exist
    if not os.path.exists(pdir):
        l.error('{0} does not exist, quitting'.format(pdir))
        return 1

    # make sure the virtualenv root exists
    if not os.path.exists(os.path.dirname(vdir)):
        os.makedirs(os.path.dirname(vdir))

    # go ahead and create the environment
    virtualenv = findpybin('virtualenv', sys.executable)
    try:
        output = getoutputoserror('{0} {1}'.format(virtualenv, vdir))
        l.debug(''.ljust(40, '='))
        l.debug(output)
        l.debug(''.ljust(40, '='))
    except OSError as e:
        l.error(str(e))
        return 1

    # plugins
    for plugin_name in args['plugins']:
        if getattr(plugins, 'install_{0}'.format(plugin_name))(args) == 1:
            return 1

    return 0


def _erase(args):
    """Remove the virtualenv associated with this project"""

    # break out various args for convenience
    vdir = args['virtualenv_dir']

    # make sure the directory exists
    if not os.path.exists(vdir):
        l.error('virtual environment does not exist, quitting')
        return 1

    # go ahead and create the environment
    shutil.rmtree(vdir)
    l.info('environment erased successfully')
    return 0


def fence():
    """Main entry point"""

    args = _get_args()
    for mode in ['activate', 'create', 'erase']:
        if args[mode]:
            l.debug('{0}ing environment with args: {1}'.format(mode[:-1], args))
            return globals()['_{0}'.format(mode)](args)


if __name__ == '__main__':
    sys.exit(fence())
