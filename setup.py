from setuptools import setup

setup(
    name='fencepy',
    version='0.3',
    description='Standardized fencing off of python virtual environments on a per-project basis',
    author='Adam Kaufman',
    author_email='kaufman.blue@gmail.com',
    url='https://github.com/ajk8/fencepy',
    download_url='https://github.com/ajk8/fencepy/tarball/0.2',
    license='MIT',
    packages=['fencepy'],
    entry_points={'console_scripts': ['fencepy = fencepy:fence']},
    test_suite='tests',
    install_requires=[
        'virtualenv>=1.11',
        'sh>=1.09'
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
