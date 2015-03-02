"""
fencepy.main

Main CLI logic
"""

import docopt
import os
import shutil
import sys
from . import plugins
from .helpers import getoutputoserror, findpybin, str2bool, py2, pyversionstr, get_shell

try:
    from ConfigParser import SafeConfigParser
except ImportError:
    from configparser import SafeConfigParser

from logging.handlers import RotatingFileHandler
import logging as l

DOCOPT = """
fencepy -- Standardized fencing off of python virtual environments on a per-project basis

Usage:
  fencepy create [options]
  fencepy activate [options]
  fencepy erase [options]

Options:
  -h --help                    Show this screen
  -v --verbose                 Print/log more verbose output
  -q --quiet                   Silence all console output
  -s --silent                  Silence ALL output, including log output (except "activate")
  -C FILE --config-file=FILE   Config file to use [default: ~/.fencepy/fencepy.conf]
  -P LIST --plugins=LIST       Comma-separated list of plugins to apply (only "create")

Path Overrides:
  -d DIR --dir=DIR             Link the fenced environment to DIR instead of the CWD
  -D DIR --virtualenv-dir=DIR  Use DIR as the root directory for the virtual environment
  -F DIR --fencepy-root=DIR    Use DIR as the root of the fencepy tree [default: ~/.fencepy]
  -G --no-git                  Don't treat the working directory as a git repository
"""


def _get_args():
    """Do all parsing and processing for command-line arguments"""

    args = docopt.docopt(DOCOPT)

    # set up the root directory
    args['--fencepy-root'] = os.path.expanduser(args['--fencepy-root'])
    if not os.path.exists(args['--fencepy-root']):
        os.mkdir(args['--fencepy-root'])

    # set up logging
    if not args['--silent']:
        f = l.Formatter('%(asctime)s [%(levelname)s] %(module)s: %(message)s')
        h = RotatingFileHandler(os.path.join(args['--fencepy-root'], 'fencepy.log'))
        h.setFormatter(f)
        l.getLogger('').addHandler(h)
    if not (args['--silent'] or args['--quiet']):
        f = l.Formatter('[%(levelname)s] %(message)s')
        h = l.StreamHandler()
        h.setFormatter(f)
        l.getLogger('').addHandler(h)

    if args['--verbose']:
        l.getLogger('').setLevel(l.DEBUG)
        l.getLogger('sh').setLevel(l.INFO)
    else:
        l.getLogger('').setLevel(l.INFO)
        l.getLogger('sh').setLevel(l.ERROR)

    # we need to do some work to get the root directory we care about here
    if not args['--dir']:
        args['--dir'] = os.getcwd()
    if not args['--no-git']:
        try:
            output = getoutputoserror('git rev-parse --show-toplevel')
            args['--dir'] = output.strip()
        except OSError as e:
            l.debug("tried to handle {0} as a git repository but it isn't one".format(args['--dir']))

    # reset the virtualenv root, if necessary
    if not args['--virtualenv-dir']:
        venv_root = os.path.join(args['--fencepy-root'], 'virtualenvs')

        # if we're one directory below the root, this logic needs to work differently
        parent = os.path.dirname(args['--dir'])
        if parent in ('/', os.path.splitdrive(parent)[0]):
            args['--virtualenv-dir'] = os.path.join(venv_root, os.path.basename(args['--dir']))

        else:
            # need the realpath here because in some circumstances windows paths get passed
            # with a '/' and others see it coming in as a '\'
            tokens = os.path.dirname(os.path.realpath(args['--dir'])).split(os.path.sep)
            tokens.reverse()
            if tokens[-1] == '':
                tokens = tokens[:-1]
            prjpart = '.'.join([os.path.basename(args['--dir']), '.'.join([d[0] for d in tokens])])
            args['--virtualenv-dir'] = os.path.join(venv_root, '-'.join((prjpart, pyversionstr())))

    # only populate the parser if there's a valid file
    config = SafeConfigParser()
    readconf = True
    if args['--config-file'] == '~/.fencepy/fencepy.conf':
        args['--config-file'] = os.path.join(args['--fencepy-root'], 'fencepy.conf')
        if not os.path.exists(args['--config-file']):
            readconf = False
    elif not os.path.exists(args['--config-file']):
        raise IOError('specified config file {0} does not exist'.format(args['--config-file']))
    if readconf:
        config.read(args['--config-file'])

    # plugins -- all false means all true
    if args['--plugins']:
        args['plugins'] = dict((key, key in args['--plugins'].split(',')) for key in plugins.PLUGINS)
    else:
        args['plugins'] = dict((key, True) for key in plugins.PLUGINS)
        if config.has_section('plugins'):
            for key, value in config.items('plugins'):
                print(key, value)
                if key not in plugins.PLUGINS:
                    raise KeyError('invalid configuration: {0} is not a valid plugin'.format(key))
                args['plugins'][key] = str2bool(value)
    return args


def _activate(args):
    """Print out the path to the appropriate activate script"""

    # break out the virtual environment directory for convenience
    vdir = args['--virtualenv-dir']

    # make sure the directory exists
    if not os.path.exists(vdir):
        l.error('virtual environment does not exist, create it with -c')
        return 1

    # unix-based shells
    shell = get_shell()
    if shell == 'fish':
        apath = os.path.join(vdir, 'bin', 'activate.fish')
    elif shell == 'csh':
        apath = os.path.join(vdir, 'bin', 'activate.csh')
    elif shell.endswith('sh'):
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
    vdir = args['--virtualenv-dir']
    pdir = args['--dir']  # p for project

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
        output = getoutputoserror('{0} -p {1} {2}'.format(virtualenv, sys.executable, vdir))
        l.debug(''.ljust(40, '='))
        l.debug(output)
        l.debug(''.ljust(40, '='))
    except OSError as e:
        l.error(str(e))
        return 1

    # plugins
    for plugin_name in [key for key, value in args['plugins'].items() if value]:
        if getattr(plugins, 'install_{0}'.format(plugin_name))(args) == 1:
            return 1

    return 0


def _erase(args):
    """Remove the virtualenv associated with this project"""

    # break out various args for convenience
    vdir = args['--virtualenv-dir']

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
