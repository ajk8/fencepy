fencepy
=======

|Development Status| |Latest Version| |Download Stats| |Python Versions| |Wheel Status|

Standardized fencing off of python virtual environments on a per-project
basis. The idea is to take a directory as an input and create and manage
a python virtual environment in a known location.

**Master on Linux**

|Travis Status| |Coveralls Status|

**Master on Windows** 

|Appveyor Status|

How does it work?
-----------------

`fencepy` is fairly simple. After parsing arguments, it calls out to the
correct copy of `virtualenv` (based on the location of the running python
interpreter) with a pre-generated base directory. Upon successful creation
of the virtual environment, it applies various modifications based on the
contents of the directory from which it was run.

Opinionated hooks
-----------------

The goal is to make this framework attractive to users of other
compatible products. For instance, as a user of git and sublime text, I
added functionality related to those.

git
~~~

If the directory provided as input (defaults to cwd) is part of a git
repository, the virtual environment created will be relative to the root
of that repository.

sublime text
~~~~~~~~~~~~

The sublime linter plugin is very easy to configure. Pointing it to a
particular installation of python is as simple as putting some json into
a configuration file. If there is a ``.sublime-project`` file in the
input directory, then it will be configured to respect the virtual
environment that is being created.

requirements.txt
~~~~~~~~~~~~~~~~

As a helpful shortcut, if there is a ``requirements.txt`` file in the
input directory, then those requirements will be installed upon
virtualenv creation.

Usage
-----

``fencepy -c``: Create a new virtual environment

``. `fencepy -a```: Activate the virtual environment in a bash-like shell

``source (fencepy -a)``: Activate the virtual environment in fish shell

``. $(fencepy -a)``: Activate the virtual environment in windows powershell

``fencepy -e``: Remove the virtual environment

Additional notes
----------------

Python versions
~~~~~~~~~~~~~~~

Both python 2 and 3 are supported. Additionally, both can be used for
one project, as they will be stored in separate directories.

Cross-platform support
~~~~~~~~~~~~~~~~~~~~~~

Both Windows and UNIX shells are supported! I have not yet figured out how
to activate in one command from within CMD.exe. If anyone knows the solution,
please let me know!

Extending fencepy
~~~~~~~~~~~~~~~~~

Additional functionality should be very easy to implement. Each of the hooks
mentioned above is implemented as a "plugin" that takes the full dict of parsed
arguments as input. Additionally, inverse cleanup methods are planned for the
future.

Alternatives
~~~~~~~~~~~~

* virtualenvwrapper_

.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/en/latest/

.. |Travis Status| image:: https://travis-ci.org/ajk8/fencepy.png?branch=master
    :target: https://travis-ci.org/ajk8/fencepy
    :alt: Travis-ci build status
.. |Coveralls Status| image:: https://coveralls.io/repos/ajk8/fencepy/badge.png?branch=master
    :target: https://coveralls.io/r/ajk8/fencepy?branch=master
    :alt: Coveralls coverage (from travis)
.. |Appveyor Status| image:: https://ci.appveyor.com/api/projects/status/qss2qb9y95i8oalc?svg=true&branch=master
    :target: https://ci.appveyor.com/project/ajk8/fencepy
    :alt: Appveyor build status
.. |Python Versions| image:: https://pypip.in/py_versions/fencepy/badge.svg
    :target: https://pypi.python.org/pypi/fencepy/
    :alt: Supported Python versions
.. |Latest Version| image:: https://pypip.in/v/fencepy/badge.png
    :target: https://pypi.python.org/pypi/fencepy/
    :alt: Latest Version
.. |Download Stats| image:: https://pypip.in/d/fencepy/badge.png
    :target: https://pypi.python.org/pypi/fencepy/
    :alt: Downloads/month
.. |Egg Status| image:: https://pypip.in/egg/fencepy/badge.svg
    :target: https://pypi.python.org/pypi/fencepy/
    :alt: Egg Status
.. |Wheel Status| image:: https://pypip.in/wheel/fencepy/badge.png
    :target: https://pypi.python.org/pypi/fencepy/
    :alt: Wheel Status
.. |License| image:: https://pypip.in/license/fencepy/badge.svg
    :target: https://pypi.python.org/pypi/fencepy/
    :alt: License
.. |Development Status| image:: https://pypip.in/status/fencepy/badge.svg
    :target: https://pypi.python.org/pypi/fencepy/
    :alt: Development Status

