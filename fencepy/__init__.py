"""
fencepy

Create a virtual environment tied to a particular directory and shortcuts to its activation.
Includes special processing if the directory is part of a git repository.  Also includes convenience
configuration for users of sublime text
"""

import argparse
import fnmatch
import json
import os
import shutil
import virtualenv
import copy
import sys
import sh

FENCEPY_ROOT = os.path.join(os.path.expanduser('~'), '.fencepy')
if not os.path.exists(FENCEPY_ROOT):
    os.mkdir(FENCEPY_ROOT)

import logging as l
l.basicConfig(filename=os.path.join(FENCEPY_ROOT, 'fencepy.log'))

VENV_ROOT = os.path.join(FENCEPY_ROOT, 'virtualenvs')
QUIET = False


def _get_args():
    """Do all parsing and processing for command-line arguments"""

    p = argparse.ArgumentParser()
    p.add_argument('-p', '--plain', action='store_true',
                   help="Don't treat the working directory as a git repository")
    p.add_argument('-d', '--dir',
                   help='Use DIR as the root path for the fenced environment instead of the CWD')
    p.add_argument('-D', '--virtualenv-dir', metavar='DIR',
                   help='Use DIR as the root directory for the virtualenv instead of the default')
    p.add_argument('-a', '--activate', action='store_true',
                   help='Print the path to the activate script in the fenced environment -- this is the default behavior')
    p.add_argument('-c', '--create', action='store_true',
                   help='Create the fenced environment')
    p.add_argument('-e', '--erase', action='store_true',
                   help='Erase the fenced environment')
    p.add_argument('-v', '--verbose', '--debug', action='store_true',
                   help='Print debug logging')
    p.add_argument('-q', '--quiet', action='store_true',
                   help='Silence all console output')
    args = vars(p.parse_args())

    # make sure we area globally quiet
    if args['quiet']:
        global QUIET
        QUIET = True

    # set up logging
    else:
        f = l.Formatter('[%(levelname)s] %(message)s')
        h = l.StreamHandler()
        h.setFormatter(f)
        l.getLogger('').addHandler(h)
    l.getLogger('').setLevel(l.DEBUG if args['verbose'] else l.INFO)

    # we need to do some work to get the root directory we care about here
    if not args['dir']:
        args['dir'] = os.getcwd()
    if not args['plain']:
        try:
            output = sh.git('rev-parse', '--show-toplevel')
            args['dir'] = str(output).strip()
        except sh.ErrorReturnCode:
            l.warning("tried to handle {0} as a git repository but it isn't one".format(args['dir']))

    # reset the virtualenv root, if necessary
    if not args['virtualenv_dir']:

        # if we're one directory below the root, this logic needs to work differently
        parent = os.path.dirname(args['dir'])
        if parent in ('/', os.path.splitdrive(parent)[0]):
            args['virtualenv_dir'] = os.path.join(VENV_ROOT, os.path.basename(args['dir']))

        else:
            tokens = os.path.dirname(args['dir']).split(os.path.sep)
            tokens.reverse()
            if tokens[-1] == '':
                tokens = tokens[:-1]
            prjpart = '.'.join([os.path.basename(args['dir']), '.'.join([d[0] for d in tokens])])
            verpart = '.'.join([str(x) for x in sys.version_info[:2]])
            args['virtualenv_dir'] = os.path.join(VENV_ROOT, prjpart, verpart)

    # set the mode properly
    modecount = [args['activate'], args['create'], args['erase']].count(True)
    if modecount > 1:
        l.error("please specify only one of -a, -c, -e")
    elif modecount == 0:
        args['activate'] = True

    return args


def _activate(args):
    """Print out the path to the appropriate activate script"""

    # break out the virtual environment directory for convenience
    vdir = args['virtualenv_dir']

    # make sure the directory exists
    if not os.path.exists(vdir):
        l.error('virtual environment does not exist, create it with -c')
        return 1

    # right now this only supports linux
    # we'll have to figure out how to support windows in the future
    shell = os.environ['SHELL']
    if shell.endswith('fish'):
        apath = os.path.join(vdir, 'bin', 'activate.fish')
    elif shell.endswith('csh'):
        apath = os.path.join(vdir, 'bin', 'activate.csh')
    else:
        apath = os.path.join(vdir, 'bin', 'activate')

    # i don't think it's possible to set the calling environment,
    # so we'll just print the path to the script
    print(apath)
    return 0


def _pseudo_merge_dict(dto, dfrom):
    """Recursively merge dict objects, overwriting any non-dict values"""

    # a quick type check
    if not type(dfrom) == dict:
        raise ValueError('non-dict passed into _psuedo_merge_dict')

    # do the work
    for k, v in dfrom.items():
        if k not in dto.keys():
            dto[k] = v

        # recurse on further dicts
        if type(dfrom[k]) == dict:
            _pseudo_merge_dict(dto[k], dfrom[k])

        # everything else can just be overwritten
        else:
            dto[k] = dfrom[k]


def _locate_subdirs(pattern, root):
    """Get a list of all subdirectories contained underneath a root"""

    ret = []
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for subdir in fnmatch.filter(dirs, pattern):
            ret.append(os.path.join(path, subdir))
    return ret


def _print(line):
    """Wrapper function for printing sh output is necessary for python 2 compatibility"""
    if not QUIET:
        print(line)


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

    # go ahead and create the environment
    virtualenv = os.path.join(os.path.dirname(sys.argv[0]), 'virtualenv')
    _print(''.ljust(40, '='))
    output = sh.Command(virtualenv)(vdir, _out=_print, _err=_print)
    output.wait()
    _print(''.ljust(40, '='))
    if output.exit_code:
        l.error('there was a problem: {0}'.format(str(output)))
        return 1

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
                'python_paths': {'linux': _locate_subdirs('site-packages', vdir)}
            }
        }
        _pseudo_merge_dict(cfg_dict, dict_data)
        json.dump(cfg_dict, open(scfg, 'w'), indent=4, separators=(', ', ': '), sort_keys=True)
        l.info('successfully configured sublime linter')

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
