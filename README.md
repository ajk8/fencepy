# fencepy

Standardized fencing off of python virtual environments on a per-project basis.  The idea is to take a directory as an input and create and manage a python virtual environment in a known location.

## Opinionated hooks

The goal is to make this framework attractive to users of other compatible products.  For instance, as a user of git and sublime text, I added functionality related to those.

### git

If the directory provided as input (defaults to cwd) is part of a git repository, the virtual environment created will be relative to the root of that repository.

### sublime text

The sublime linter plugin is very easy to configure.  Pointing it to a particular installation of python is as simple as putting some json into a configuration file.  If there is a `.sublime-project` file in the input directory, then it will be configured to respect the virtual environment that is being created.

### requirements.txt

As a helpful shortcut, if there is a `requirements.txt` file in the input directory, then those requirements will be installed upon virtualenv creation.

## Usage

* Create a new virtual environment

```fencepy -c```

* Activate the virtual environment in a bash-like shell

```. `fencepy -a` ```

* Activate the virtual environment in fish shell

```. (fencepy -a)```

* Remove the virtual environment

```fencepy -e```

## Additional notes

During initial implementation, care was taken to make the library mostly platform-independent.  However, it has not been tested with anything other than linux and is not expected to function in other environments without some work.
