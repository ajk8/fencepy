import sys
import re
import os
from setuptools import setup


def get_version():
    version_file = open(os.path.join('fencepy', 'main.py')).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

pkgversion = get_version()

setup(
    name='fencepy',
    version=pkgversion,
    description='Standardized fencing off of python virtual environments on a per-project basis',
    author='Adam Kaufman',
    author_email='kaufman.blue@gmail.com',
    url='https://github.com/ajk8/fencepy',
    download_url='https://github.com/ajk8/fencepy/tarball/' + pkgversion,
    license='MIT',
    packages=['fencepy'],
    package_data={'fencepy': ['fencepy.conf.default']},
    entry_points={'console_scripts': ['fencepy=fencepy:fence',
                                      'fencepy-%s.%s=fencepy:fence' % sys.version_info[:2]]},
    test_suite='tests',
    install_requires=[
        'virtualenv>=12.0.7',
        'psutil>=2.2.1',
        'docopt>=0.6.2',
        'funcy>=1.5'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development'
    ],
    keywords='virtualenv development'
)
