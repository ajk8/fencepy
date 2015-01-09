fencepy
=======

|Build Status| |Coverage Status| |Development Status| |Latest Version| |Download Stats| |Python Versions|

Standardized fencing off of python virtual environments on a per-project
basis. The idea is to take a directory as an input and create and manage
a python virtual environment in a known location.

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

-  Create a new virtual environment

``fencepy -c``

-  Activate the virtual environment in a bash-like shell

``. `fencepy -a```

-  Activate the virtual environment in fish shell

``. (fencepy -a)``

-  Remove the virtual environment

``fencepy -e``

Additional notes
----------------

Python versions
~~~~~~~~~~~~~~~

Both python 2 and 3 are supported. Additionally, both can be used for
one project, as they will be stored in separate directories.

Cross-platform support
~~~~~~~~~~~~~~~~~~~~~~

During initial implementation, care was taken to make the library mostly
platform-independent. However, it has since drifted in a linux-specific
direction. By eliminating use of the `sh` module, it could be made to work
in windows. If anyone is interested, feel free to submit a pull request.

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

.. |Build Status| image:: https://travis-ci.org/ajk8/fencepy.png?branch=master
    :target: https://travis-ci.org/ajk8/fencepy
    :alt: Build status
.. |Coverage Status| image:: https://coveralls.io/repos/ajk8/fencepy/badge.png?branch=master
    :target: https://coveralls.io/r/ajk8/fencepy?branch=master
    :alt: Testing coverage
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
