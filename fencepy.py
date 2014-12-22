#!/usr/bin/python

import argparse
import commands
import fnmatch
import json
import os
import shutil

FENCEPY_ROOT = os.path.join(os.path.expanduser('~'), '.fencepy')
if not os.path.exists(FENCEPY_ROOT):
    os.mkdir(FENCEPY_ROOT)

import logging as l
l.basicConfig(filename=os.path.join(FENCEPY_ROOT, 'fencepy.log'))

VENV_ROOT = os.path.join(FENCEPY_ROOT, 'virtualenvs')

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

    # set up logging
    if not args['quiet']:
        l.getLogger('').addHandler(l.StreamHandler())
    l.getLogger('').setLevel(l.DEBUG if args['verbose'] else l.INFO)

    # we need to do some work to get the root directory we care about here
    if not args['dir']:
        args['dir'] = os.getcwd()
    if not args['plain']:
        s, o = commands.getstatusoutput('git rev-parse --show-toplevel')
        if not s:
            args['dir'] = o.strip()
        else:
            l.error("tried to handle {0} as a git repository but it isn't one".format(args['dir']))

    # reset the virtualenv root, if necessary
    if not args['virtualenv_dir']:
        tokens = os.path.dirname(args['dir']).split(os.path.sep)
        tokens.reverse()
        if tokens[-1] == '':
            tokens = tokens[:-1]
        suffix = '.'.join([d[0] for d in tokens])
        args['virtualenv_dir'] = os.path.join(VENV_ROOT, '.'.join([os.path.basename(args['dir']), suffix]))

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
        if not dto.has_key(k):
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


def _create(args):
    """Create a virtualenv for the current project"""

    # break out various args for convenience
    vdir = args['virtualenv_dir']
    pdir = args['dir'] # p for project

    # make sure the directory doesn't already exist
    if os.path.exists(vdir):
        l.error('virtual environment already exists, quitting')
        return 1

    # go ahead and create the environment
    s, o = commands.getstatusoutput('virtualenv {0}'.format(vdir))
    if not s:
        l.info('environment created successfully')

    else:
        l.error('there was a problem: {0}'.format(o))
        return 1

    # install requirements, if they exist
    rtxt = os.path.join(pdir, 'requirements.txt')
    if os.path.exists(rtxt):
        l.info('loading requirements from {0}, this can take awhile'.format(rtxt))
        pip = os.path.join(vdir, 'bin', 'pip')
        s, o = commands.getstatusoutput('{0} install -r {1}'.format(pip, rtxt))
        print(o)
        if s:
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
    fence()
