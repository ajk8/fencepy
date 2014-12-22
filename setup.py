from distutils.core import setup

setup(
    name='fencepy',
    version='0.1',
    description='Standaradized fencing off of python virtual environments on a per-project basis',
    author='Adam Kaufman',
    author_email='ajk.eight@gmail.com',
    url='https://github.com/ajk8/fencepy',
    packages=['fencepy'],
    entry_points={'console_scripts': ['fencepy = fencepy:fence']}
)
