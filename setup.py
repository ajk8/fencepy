import sys
from setuptools import setup
from imp import find_module, load_module

PROJECT_NAME = 'fencepy'
GITHUB_USER = 'ajk8'
GITHUB_ROOT = 'https://github.com/{}/{}'.format(GITHUB_USER, PROJECT_NAME)

found = find_module('_version', [PROJECT_NAME])
_version = load_module('_version', *found)


setup(
    name=PROJECT_NAME,
    version=_version.__version__,
    description='Standardized fencing off of python virtual environments on a per-project basis',
    author='Adam Kaufman',
    author_email='kaufman.blue@gmail.com',
    url=GITHUB_ROOT,
    download_url='{0}/tarball/{1}'.format(GITHUB_ROOT, _version.__version__),
    license='MIT',
    packages=[PROJECT_NAME],
    package_data={PROJECT_NAME: ['fencepy.conf.default']},
    entry_points={'console_scripts': [
        'fencepy=fencepy:fence',
        'fencepy-{0}.{1}=fencepy:fence'.format(*sys.version_info[:2])
    ]},
    install_requires=[
        'virtualenv>=12.0.7',
        'psutil>=2.2.1',
        'docopt>=0.6.2',
        'funcy>=1.5',
        'six>=1.10.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Shells',
        'Topic :: Terminals',
        'Topic :: Terminals :: Terminal Emulators/X Terminals',
        'Topic :: Utilities'
    ],
    keywords='fencepy virtualenv virtual environment development project'
)
