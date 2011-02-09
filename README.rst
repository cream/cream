Cream Desktop Environment
=========================

How to install Cream?
---------------------

You need:
 * virtualenv

Installation
~~~~~~~~~~~~

git clone git://github.com/cream/cream.git
cd cream/
make setup

Usage
~~~~~

Before you can use Cream, always make sure to activate the virtualenv:

source dev/bin/activate

Updating
~~~~~~~~

If a package was added or files were added/removed, make sure to run:

make develop
