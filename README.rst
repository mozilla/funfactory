funfactory is what makes `playdoh`_ fun. You import it within a Django
`manage.py`_ file and it sets up the playdoh environment and configures some
settings.

Install
=======

::

    pip install funfactory

What is it?
===========

funfactory is the core of `playdoh`_, Mozilla's Django starter kit.
funfactory is *not* a collection of standalone apps.

Check out the `playdoh docs`_ for a complete user guide.

funfactory is also the name of a script that automates the installation of a
new Playdoh app.  Check out ``funfactory --help`` for more info.

.. _`playdoh`: https://github.com/mozilla/playdoh
.. _`playdoh docs`: http://playdoh.readthedocs.org/
.. _`manage.py`: https://github.com/mozilla/playdoh/blob/master/manage.py

Hacking
=======

To develop new features for playdoh core, you'll want to hack on funfactory!
To run the test suite, first install `tox`_ then cd into the root dir
and type the ``tox`` command.  The ``tox.ini`` will handle the rest.

.. _`tox`: http://tox.readthedocs.org/

.. note::
    if you supply a different playdoh remote URL or a different
    branch or something, remember to delete the ``.playdoh/`` directory
    between tests for a clean slate.

To try out cutting edge funfactory features in a real playdoh app, you can use
the develop command to install a link to the files within your virtualenv::

  workon the-playdoh-clone
  pushd ~/your/path/to/funfactory
  python setup.py develop
  popd

Test Suite Environment
======================

Here are some environment variables that are acknowledged by the test suite:

**FF_DB_USER**
  MySQL db user to run manage.py test. Defaults to ``root``.

**FF_DB_PASS**
  MySQL user password for manage.py test. Defaults to an empty string.

**FF_DB_NAME**
  MySQL db name for manage.py test. Defaults to ``_funfactory_test``.

**FF_PLAYDOH_REMOTE**
  Git qualified URL for playdoh repo. Defaults to ``git://github.com/mozilla/playdoh.git``.

**FF_PLAYDOH_BRANCH**
  Default branch to pull and update. Defaults to ``master``.
