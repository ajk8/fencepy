from unittest import TestCase
import tempfile
import fencepy
import os
import shutil
import copy
import sys
import sh
from contextlib import contextmanager
if sys.version.startswith('2'):
    from StringIO import StringIO
else:
    from io import StringIO

@contextmanager
def redirected(out=sys.stdout, err=sys.stderr):
    saved = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = out, err
    try:
        yield
    finally:
        sys.stdout, sys.stderr = saved

PROJECT_NAME = 'fencepytest'
ORIGINAL_DIR = os.getcwd()
ORIGINAL_ARGV = copy.copy(sys.argv)

class TestFencepy(TestCase):

    def _fence(self, *args):
        sys.argv = ['fencepy'] + list(args)
        ret = fencepy.fence()
        sys.argv = ORIGINAL_ARGV
        return ret

    def _get_arg_dict(self, *args):
        sys.argv = ['fencepy', '-q'] + list(args)
        ret = fencepy._get_args()
        sys.argv = ORIGINAL_ARGV
        return ret

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.pdir = os.path.join(self.tempdir, PROJECT_NAME)
        os.mkdir(self.pdir)
        os.chdir(self.pdir)
        self.default_args = self._get_arg_dict()

    def tearDown(self):
        if os.path.exists(self.default_args['virtualenv_dir']):
            shutil.rmtree(self.default_args['virtualenv_dir'])
        os.chdir(ORIGINAL_DIR)
        shutil.rmtree(self.tempdir)

    def _create_and_assert(self, *args):
        ret = self._fence('-q', '-c', *args)
        self.assertEqual(ret, 0, 'create command failed')
        self.assertTrue(os.path.exists(self.default_args['virtualenv_dir']))

    def test_create_plain(self):
        self._create_and_assert('-p')

    def test_create_nongit_without_plain(self):
        self._create_and_assert()

    def test_create_git(self):
        sh.git.init('.')
        os.mkdir('test')
        os.chdir('test')
        self._create_and_assert()

    def test_create_with_pdir_does_exist(self):
        project_name = 'project'
        project_dir = os.path.join(self.tempdir, project_name)
        os.mkdir(project_dir)
        args = self._get_arg_dict('-d', project_dir)
        self.assertTrue(project_name in args['virtualenv_dir'])
        ret = self._fence('-q', '-c', '-d', project_dir)
        self.assertEqual(ret, 0, 'create command failed')
        self.assertTrue(os.path.exists(args['virtualenv_dir']))
        shutil.rmtree(args['virtualenv_dir'])

    def test_create_with_pdir_does_not_exist(self):
        project_name = 'notarealpath'
        project_dir = os.path.join(tempfile.gettempdir(), project_name)
        args = self._get_arg_dict('-d', project_dir)
        self.assertTrue(project_name in args['virtualenv_dir'])
        ret = self._fence('-q', '-c', '-d', project_dir)
        self.assertNotEqual(ret, 0, 'create command should not succeed')
        self.assertFalse(os.path.exists(args['virtualenv_dir']))

    def test_create_with_vdir(self):
        vdir = os.path.join(self.tempdir, 'virtualenv')
        args = self._get_arg_dict('-D', vdir)
        self.assertEqual(vdir, args['virtualenv_dir'])
        ret = self._fence('-q', '-c', '-D', vdir)
        self.assertEqual(ret, 0, 'create command failed')
        self.assertTrue(os.path.exists(vdir))

    def test_erase(self):
        self.test_create_plain()
        ret = self._fence('-q', '-e')
        self.assertEqual(ret, 0, 'erase command failed')
        self.assertFalse(os.path.exists(self.default_args['virtualenv_dir']))

    def _test_activate(self, shell, script):
        self.test_create_plain()
        os.environ['SHELL'] = shell
        tempout = StringIO()
        with redirected(out=tempout):
            ret = self._fence('-q', '-a')
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


