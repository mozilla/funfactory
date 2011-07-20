funfactory is the what makes `playdoh`_ fun. You import it within a Django `manage.py`_ file and it sets up the playdoh environment and configures some
settings.
Any substantial part of playdoh's *core* should be contained within funfactory.  However, it is not a collection of standalone apps.
Check out the `playdoh docs`_ for a complete user guide.

.. _`playdoh`: https://github.com/mozilla/playdoh
.. _`playdoh docs`: http://playdoh.readthedocs.org/
.. _`manage.py`: https://github.com/mozilla/playdoh/blob/base/manage.py

Hacking
=======

To develop new features for playdoh core, you'll want to hack on funfactory!
To run the test suite, first install `tox`_ then cd into the root dir
and type the ``tox`` command.  The ``tox.ini`` will handle the rest.

.. _`tox`: http://tox.readthedocs.org/

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
