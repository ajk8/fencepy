"""
fencepy.main

Main CLI logic
"""

import docopt
import os
import shutil
import sys
import psutil
from funcy import memoize
from . import plugins
from .helpers import getoutputoserror, findpybin, str2bool, pyversionstr, get_shell

try:
    from ConfigParser import SafeConfigParser
except ImportError:
    from configparser import SafeConfigParser

from logging.handlers import RotatingFileHandler
import logging as l

__version__ = '0.7.0'

DOCOPT = """
fencepy -- Standardized fencing off of python virtual environments on a per-project basis

Usage:
  fencepy create [options]
  fencepy activate [options]
  fencepy update [options]
  fencepy erase [options]
  fencepy nuke [options]
  fencepy genconfig
  fencepy help
  fencepy version

Options:
  -v --verbose                      Print/log more verbose output
  -q --quiet                        Silence all console output
  -s --silent                       Silence ALL output, including log output (except "activate")
  -C FILE --config-file=FILE        Config file to use [default: ~/.fencepy/fencepy.conf]
  -P LIST --plugins=LIST            Comma-separated list of plugins to apply (only "create")
  -S DIR --sublime-project-dir=DIR  Search in DIR for .sublime-project files

Path Overrides:
  -d DIR --dir=DIR                  Link the fenced environment to DIR instead of the CWD
  -D DIR --virtualenv-dir=DIR       Use DIR as the root directory for the virtual environment
  -F DIR --fencepy-root=DIR         Use DIR as the root of the fencepy tree [default: ~/.fencepy]
  -G --no-git                       Don't treat the working directory as a git repository
"""


@memoize
def _get_parsed_config_file(filepath):
    """Return a SafeConfigParser loaded with the data from a config file at filepath"""
    ret = SafeConfigParser()
    ret.read(filepath)
    return ret


@memoize
def _get_default_config_file():
    """Return the path to fencepy's default config file"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fencepy.conf.default')


@memoize
def _get_default_config_parsed():
    """Return a SafeConfigParser loaded with the default config"""
    return _get_parsed_config_file(_get_default_config_file())


def _items_to_dict(items):
    """Return a dict of items taken from a section of a SafeConfigParser"""
    return dict((key, value) for key, value in items)


def _fill_in_plugins_config(args, config=None):
    """Add a plugins config structure to args"""

    # fill in plugins config, starting with the default fencepy conf
    allplugins = True
    args['plugins'] = {}
    for plugin in plugins.PLUGINS:

        # the default config will have a complete list of necessary parameters -- no need to reinvent the wheel
        args['plugins'][plugin] = _items_to_dict(_get_default_config_parsed().items(plugin))
        args['plugins'][plugin]['enabled'] = False

        # override with anything that comes from the passed in config file
        if config is not None and config.has_section(plugin):
            allplugins = False
            args['plugins'][plugin] = _items_to_dict(config.items(plugin))
            args['plugins'][plugin]['enabled'] = str2bool(args['plugins'][plugin]['enabled'])

        # the config file can be overridden by the command line
        if args['--plugins']:
            args['plugins'][plugin]['enabled'] = True if plugin in args['--plugins'].split(',') else False

        # if no plugins are enabled based on input, then all plugins are enabled (default behavior)
        if args['plugins'][plugin]['enabled']:
            allplugins = False

    # default enabling of plugins
    if allplugins:
        for plugin in plugins.PLUGINS:
            args['plugins'][plugin]['enabled'] = True

    # add in any stuff directly from the command line
    if args['--sublime-project-dir']:
        args['plugins']['sublime']['project-dir'] = args['--sublime-project-dir']

    return args


@memoize
def _get_virtualenv_root(fencepy_root):
    """Return the path to fencepy's virtualenv subdirectory"""
    return os.path.join(fencepy_root, 'virtualenvs')


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
        except OSError:
            l.debug("tried to handle {0} as a git repository but it isn't one".format(args['--dir']))

    # reset the virtualenv root, if necessary
    if not args['--virtualenv-dir']:
        venv_root = _get_virtualenv_root(args['--fencepy-root'])

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
    config = None
    readconf = True
    if args['--config-file'] == '~/.fencepy/fencepy.conf':
        args['--config-file'] = os.path.join(args['--fencepy-root'], 'fencepy.conf')
        if not os.path.exists(args['--config-file']):
            readconf = False
    elif not os.path.exists(args['--config-file']):
        raise IOError('specified config file {0} does not exist'.format(args['--config-file']))
    if readconf:
        config = _get_parsed_config_file(args['--config-file'])

    # fill in the plugins config
    _fill_in_plugins_config(args, config)

    return args


def _activate(args):
    """Print out the path to the appropriate activate script"""

    # break out the virtual environment directory for convenience
    vdir = args['--virtualenv-dir']

    # make sure the directory exists
    if not os.path.exists(vdir):
        l.error('virtual environment does not exist, please execute fencepy create')
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


def _plugins(args):
    """Execute the plugin routines required by command line arguments"""

    # plugins
    retval = 0
    for plugin in plugins.PLUGINS:
        if plugins.install(plugin, args) == 1:
            retval = 1

    return retval


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
        l.info('creating {0}'.format(args['--virtualenv-dir']))
        output = getoutputoserror('{0} -p {1} {2}'.format(virtualenv, sys.executable, vdir))
        l.debug(''.ljust(40, '='))
        l.debug(output)
        l.debug(''.ljust(40, '='))
    except OSError as e:
        l.error(str(e))
        return 1

    # finish up with the plugins
    l.info('using plugins: {0}'.format(', '.join([x for x in plugins.PLUGINS if args['plugins'][x]['enabled']])))
    return _plugins(args)


def _update(args):
    """Just run the plugins again"""
    return _plugins(args)


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


def _nuke(args):
    """Remove ALL fencepy virtualenvs"""

    # make sure the user really wants to do this
    answer = input('You are about to blow away everything fencepy owns. Are you sure? [y/N]')
    if answer.lower() not in ['y', 'yes']:
        print('Quitting')
        return 0

    # blow it away
    venv_root = _get_virtualenv_root(args['--fencepy-root'])
    if os.path.exists(venv_root):
        shutil.rmtree(venv_root)

    return 0


def _genconfig(args):
    """Generate a default config file in the fencepy root directory"""

    fdir = args['--fencepy-root']
    cfile = os.path.join(fdir, 'fencepy.conf')

    if os.path.exists(cfile):
        l.info('backing up {0}'.format(cfile))
        i = 0
        while True:
            bak = '{0}.bak.{1}'.format(cfile, i)
            if not os.path.exists(bak):
                shutil.move(cfile, bak)
                break
    l.info('generating {0}'.format(cfile))
    shutil.copy(_get_default_config_file(), cfile)

    return 0


def fence():
    """Main entry point"""

    args = _get_args()

    # override default help functionality
    if args['help']:
        print(DOCOPT)
        return 0

    elif args['version']:
        print('{0} v{1} [{2}]'.format(
            os.path.abspath(psutil.Process(os.getpid()).cmdline()[1]), __version__, pyversionstr()
        ))
        return 0

    # do a main action
    for mode in ['activate', 'create', 'update', 'erase', 'nuke', 'genconfig']:
        if args[mode]:
            l.debug('{0}ing environment with args: {1}'.format(mode[:-1], args))
            return globals()['_{0}'.format(mode)](args)
