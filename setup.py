from setuptools import setup
import sys

pkgversion = '0.5.0'

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
    entry_points={'console_scripts': ['fencepy=fencepy:fence',
                                      'fencepy-%s.%s=fencepy:fence' % sys.version_info[:2]]},
    test_suite='tests',
    install_requires=[
        'virtualenv>=12.0.7',
        'psutil>=2.2.1',
        'docopt>=0.6.2'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
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
