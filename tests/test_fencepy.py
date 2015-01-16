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
from fencepy.helpers import getoutputoserror, redirected, py3
if py3():
    from io import StringIO
else:
    from StringIO import StringIO

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

    def _get_arg_dict(self, *args):
        # always include the overridden fencepy directory
        # no logging, since that breaks tests in Windows (with overridden fencepy dir)
        sys.argv = ['fencepy', '-F', self.fdir, '-s'] + list(args)
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
        if os.path.exists(self.default_args['virtualenv_dir']):
            shutil.rmtree(self.default_args['virtualenv_dir'])
        os.chdir(ORIGINAL_DIR)
        shutil.rmtree(self.tempdir)

    def _create_and_assert(self, *args):
        ret = self._fence('-c', *args)
        self.assertEqual(ret, 0, 'create command failed')
        self.assertTrue(os.path.exists(self.default_args['virtualenv_dir']))

    def test_create_plain(self):
        self._create_and_assert('-p')

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
        self.assertTrue(project_name in args['virtualenv_dir'])
        ret = self._fence('-c', '-d', project_dir)
        self.assertEqual(ret, 0, 'create command failed')
        self.assertTrue(os.path.exists(args['virtualenv_dir']))
        shutil.rmtree(args['virtualenv_dir'])

    def test_create_with_pdir_does_not_exist(self):
        project_name = 'notarealpath'
        project_dir = os.path.join(tempfile.gettempdir(), project_name)
        args = self._get_arg_dict('-d', project_dir)
        self.assertTrue(project_name in args['virtualenv_dir'])
        ret = self._fence('-c', '-d', project_dir)
        self.assertNotEqual(ret, 0, 'create command should not succeed')
        self.assertFalse(os.path.exists(args['virtualenv_dir']))

    def test_create_with_vdir(self):
        vdir = os.path.join(self.tempdir, 'virtualenv')
        args = self._get_arg_dict('-D', vdir)
        self.assertEqual(vdir, args['virtualenv_dir'])
        ret = self._fence('-c', '-D', vdir)
        self.assertEqual(ret, 0, 'create command failed')
        self.assertTrue(os.path.exists(vdir))

    def test_create_with_sublime(self):
        testsdir = os.path.dirname(os.path.realpath(__file__))
        defaultfile = os.path.join(testsdir, 'sublime-project.template')
        configfile = os.path.join(self.pdir, '{0}.sublime-project'.format(self.pname))
        shutil.copy(defaultfile, configfile)
        self.test_create_plain()

        # in windows, this path will have \\ instead of \
        path = self.default_args['virtualenv_dir']
        if platform.system() == 'Windows':
            path = path.replace('\\', '\\\\')
        self.assertTrue(path in open(configfile).read())

    def test_create_with_requirements(self):
        open(os.path.join(self.pdir, 'requirements.txt'), 'w').write('requests')
        self.test_create_plain()
        requests_installed = False
        for path, dirs, files in os.walk(self.default_args['virtualenv_dir']):
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
        ret = self._fence('-e')
        self.assertEqual(ret, 0, 'erase command failed')
        self.assertFalse(os.path.exists(self.default_args['virtualenv_dir']))

    def test_erase_does_not_exist(self):
        ret = self._fence('-e')
        self.assertEqual(ret, 1, 'there should be nothing to erase')
        self.assertFalse(os.path.exists(self.default_args['virtualenv_dir']))

    # This can only be used to test for unix-base shells. There is
    # no way to reliably test for .bat and .ps1 because the derivation
    # method depends on functions being available on the path
    def _test_activate(self, shell, script):
        self.test_create_plain()
        os.environ['SHELL'] = shell
        tempout = StringIO()
        with redirected(out=tempout):
            ret = self._fence('-a')
            output = tempout.getvalue()
        self.assertEqual(ret, 0, 'activate printing failed')
        self.assertTrue(self.default_args['virtualenv_dir'] in output)
        self.assertTrue(script in output)

    def test_activate_fish(self):
        self._test_activate('fish', 'activate.fish')

    def test_activate_csh(self):
        self._test_activate('csh', 'activate.csh')

    def test_activate_bash(self):
        self._test_activate('bash', 'activate')

    def test_multiple_modes(self):
        with raises(RuntimeError):
            ret = self._fence('-a', '-c', '-e')

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
