from unittest import TestCase
import tempfile
import fencepy
import os
import shutil
import copy
import sys
import platform
import uuid
from py.test import raises
from docopt import DocoptExit
from fencepy.helpers import getoutputoserror, redirected
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

ORIGINAL_DIR = os.getcwd()
ORIGINAL_ARGV = copy.copy(sys.argv)


class TestFencepy(TestCase):

    def _fence(self, *args):
        # always include the overridden fencepy directory
        # no logging, since that breaks tests in Windows (with overridden fencepy dir)
        sys.argv = ['fencepy', '-F', self.fdir, '-s'] + list(args)
        ret = fencepy.fence()
        sys.argv = ORIGINAL_ARGV
        return ret

    def _fence_no_options(self, *args):
        # help doesn't work with any options
        sys.argv = ['fencepy'] + list(args)
        ret = fencepy.fence()
        sys.argv = ORIGINAL_ARGV
        return ret

    def _get_arg_dict(self, *args):
        # always include the overridden fencepy directory
        # no logging, since that breaks tests in Windows (with overridden fencepy dir)
        # also, include "create" so that some command is included
        sys.argv = ['fencepy', 'create', '-F', self.fdir, '-s'] + list(args)
        ret = fencepy.main._get_args()
        sys.argv = ORIGINAL_ARGV
        return ret

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.fdir = os.path.join(self.tempdir, 'fencepy')
        self.pname = str(uuid.uuid4())
        self.pdir = os.path.join(self.tempdir, self.pname)
        os.mkdir(self.pdir)
        os.chdir(self.pdir)
        self.default_args = self._get_arg_dict()

    def tearDown(self):
        if os.path.exists(self.default_args['--virtualenv-dir']):
            shutil.rmtree(self.default_args['--virtualenv-dir'])
        os.chdir(ORIGINAL_DIR)
        shutil.rmtree(self.tempdir)

    def _create_and_assert(self, *args):
        ret = self._fence('create', *args)
        self.assertEqual(ret, 0, 'create command failed')
        self.assertTrue(os.path.exists(self.default_args['--virtualenv-dir']))

    def test_create_plain(self):
        self._create_and_assert('-G')

    def test_create_nongit_without_plain(self):
        self._create_and_assert()

    def test_create_git(self):
        getoutputoserror('git init .')
        os.mkdir('test')
        os.chdir('test')
        self._create_and_assert()

    def test_create_with_pdir_does_exist(self):
        project_name = 'project'
        project_dir = os.path.join(self.tempdir, project_name)
        os.mkdir(project_dir)
        args = self._get_arg_dict('-d', project_dir)
        self.assertTrue(project_name in args['--virtualenv-dir'])
        ret = self._fence('create', '-d', project_dir)
        self.assertEqual(ret, 0, 'create command failed')
        self.assertTrue(os.path.exists(args['--virtualenv-dir']))
        shutil.rmtree(args['--virtualenv-dir'])

    def test_create_with_pdir_does_not_exist(self):
        project_name = 'notarealpath'
        project_dir = os.path.join(tempfile.gettempdir(), project_name)
        args = self._get_arg_dict('-d', project_dir)
        self.assertTrue(project_name in args['--virtualenv-dir'])
        ret = self._fence('create', '-d', project_dir)
        self.assertNotEqual(ret, 0, 'create command should not succeed')
        self.assertFalse(os.path.exists(args['--virtualenv-dir']))

    def test_create_with_vdir(self):
        vdir = os.path.join(self.tempdir, 'virtualenv')
        args = self._get_arg_dict('-D', vdir)
        self.assertEqual(vdir, args['--virtualenv-dir'])
        ret = self._fence('create', '-D', vdir)
        self.assertEqual(ret, 0, 'create command failed')
        self.assertTrue(os.path.exists(vdir))

    def test_create_with_sublime(self):
        testsdir = os.path.dirname(os.path.realpath(__file__))
        defaultfile = os.path.join(testsdir, 'sublime-project.template')
        configfile = os.path.join(self.pdir, '{0}.sublime-project'.format(self.pname))
        shutil.copy(defaultfile, configfile)
        self.test_create_plain()

        # in windows, this path will have \\ instead of \
        path = self.default_args['--virtualenv-dir']
        if platform.system() == 'Windows':
            path = path.replace('\\', '\\\\')
        self.assertTrue(path in open(configfile).read())

    def test_create_with_requirements(self):
        open(os.path.join(self.pdir, 'requirements.txt'), 'w').write('requests')
        self.test_create_plain()
        requests_installed = False
        for path, dirs, files in os.walk(self.default_args['--virtualenv-dir']):
            if 'requests' in dirs:
                requests_installed = True
                break
        self.assertTrue(requests_installed, 'requests module is not installed')

    def test_create_twice(self):
        self.test_create_plain()
        with raises(AssertionError):
            self.test_create_plain()

    def test_erase(self):
        self.test_create_plain()
        ret = self._fence('erase')
        self.assertEqual(ret, 0, 'erase command failed')
        self.assertFalse(os.path.exists(self.default_args['--virtualenv-dir']))

    def test_erase_does_not_exist(self):
        ret = self._fence('erase')
        self.assertEqual(ret, 1, 'there should be nothing to erase')
        self.assertFalse(os.path.exists(self.default_args['--virtualenv-dir']))

    # Since the shell is derived from pid, this can only be generically tested
    # Full coverage remains elusive
    def test_activate(self):
        self.test_create_plain()
        tempout = StringIO()
        with redirected(out=tempout):
            ret = self._fence('activate')
        output = tempout.getvalue()
        self.assertEqual(ret, 0, 'activate printing failed')
        self.assertTrue(self.default_args['--virtualenv-dir'] in output)
        self.assertTrue('activate' in output)

    def test_multiple_modes(self):
        with raises(DocoptExit):
            ret = self._fence('activate', 'create', 'erase')

    def test_specify_plugins(self):
        self.assertTrue(self.default_args['plugins']['requirements'])
        self.assertTrue(self.default_args['plugins']['ps1'])
        self.assertTrue(self.default_args['plugins']['sublime'])
        args = self._get_arg_dict('-P', 'requirements')
        self.assertTrue(args['plugins']['requirements'])
        self.assertFalse(args['plugins']['ps1'])
        self.assertFalse(args['plugins']['sublime'])
        args = self._get_arg_dict('-P', 'requirements,ps1')
        self.assertTrue(args['plugins']['requirements'])
        self.assertTrue(args['plugins']['ps1'])
        self.assertFalse(args['plugins']['sublime'])

        lines = ['[plugins]', 'requirements = false']
        open(os.path.join(self.fdir, 'fencepy.conf'), 'w').write(os.linesep.join(lines))
        args = self._get_arg_dict()
        self.assertFalse(args['plugins']['requirements'])
        self.assertTrue(args['plugins']['ps1'])
        self.assertTrue(args['plugins']['sublime'])

    def test_help(self):
        tempout = StringIO()
        with redirected(out=tempout):
            ret = self._fence_no_options('help')
        output = tempout.getvalue()
        self.assertTrue(output.strip().startswith('fencepy'))

    def _test_nuke_with_answer(self, answer, assertion):
        venv_root = fencepy.main._get_virtualenv_root(self.fdir)
        if not os.path.exists(venv_root):
            self._fence('create')
        original_input = __builtins__['input']
        __builtins__['input'] = lambda _: answer
        self._fence('nuke')
        __builtins__['input'] = original_input
        self.assertEqual(os.path.exists(venv_root), assertion)

    def test_nuke(self):
        for answer, assertion in [
            ('y', False),
            ('Y', False),
            ('yes', False),
            ('yEs', False),
            ('', True),
            ('n', True),
            ('No', True),
            ('asdf#$*!', True)
        ]:
            self._test_nuke_with_answer(answer, assertion)
