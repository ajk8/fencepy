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
This has proven to be an unstable build environment. Keeping it here for
ease of checking up on the status manually.

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

oh-my-zsh
~~~~~~~~~

If you use ``oh-my-zsh``, when you set up your first fencepy environment, it will
configure some shortcuts for you::

    fpadd -> fencepy create
    fpnew -> fencepy create
    fpsrc -> . `fencepy activate`
    fpup  -> fencepy update
    fpdel -> fencepy erase

Quickstart
-----

``fencepy`` manages virtual environments based on the directory each environment is linked to.  So, in order to act on a virtual environment, you simply have to be in the directory that it applies to and run a ``fencepy`` command.  To get started, install ``fencepy`` with ``pip``:

.. code::

    $ sudo pip install fencepy
    
Then you can create and activate virtual environment with a few simple commands:

.. code::

    $ cd <project_dir>
    $ fencepy create
    $ . `fencepy activate`
    
These commands are universal, which is to say they never change, regardless of the project you're working on (and thus are *very* ``<ctrl-r>``-friendly).  Any time you want to get back to your virtual environment, it looks just the same, without the creation:

.. code::

    $ cd <project_dir>
    $ . `fencepy activate`
    
If, for any reason, you need to start fresh, simply blow it away and recreate:

.. code::

    $ cd <project_dir>
    $ fencepy erase
    $ fencepy create

See ``fencepy help`` for more information on these and all the other functions that ``fencepy`` has to offer!

Additional notes
----------------

Python versions
~~~~~~~~~~~~~~~

Both python 2 and 3 are supported. Additionally, both can be used for
one project, as they will be stored in separate directories.

Cross-platform support
~~~~~~~~~~~~~~~~~~~~~~

Both Windows and *nix shells are supported!

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

.. |Travis Status| image:: https://img.shields.io/travis/ajk8/fencepy/master.svg
    :target: https://travis-ci.org/ajk8/fencepy
    :alt: Travis-ci build status
.. |Coveralls Status| image:: https://img.shields.io/coveralls/ajk8/fencepy/master.svg
    :target: https://coveralls.io/r/ajk8/fencepy?branch=master
    :alt: Coveralls coverage (from travis)
.. |Appveyor Status| image:: https://img.shields.io/appveyor/ci/ajk8/fencepy/master.svg
    :target: https://ci.appveyor.com/project/ajk8/fencepy
    :alt: Appveyor build status
.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/fencepy.svg
    :target: https://pypi.python.org/pypi/fencepy/
    :alt: Supported Python versions
.. |Latest Version| image:: https://img.shields.io/pypi/v/fencepy.svg
    :target: https://pypi.python.org/pypi/fencepy/
    :alt: Latest Version
.. |Download Stats| image:: https://img.shields.io/pypi/dm/fencepy.svg
    :target: https://pypi.python.org/pypi/fencepy/
    :alt: Downloads/month
.. |Wheel Status| image:: https://img.shields.io/pypi/wheel/fencepy.svg
    :target: https://pypi.python.org/pypi/fencepy/
    :alt: Wheel Status
.. |License| image:: https://img.shields.io/pypi/l/fencepy.svg
    :target: https://pypi.python.org/pypi/fencepy/
    :alt: License
.. |Development Status| image:: https://img.shields.io/pypi/status/fencepy.svg
    :target: https://pypi.python.org/pypi/fencepy/
    :alt: Development Status
