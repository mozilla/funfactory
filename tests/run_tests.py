import os
import sys

import nose


__test__ = False  # Not a test to be collected by Nose itself.


if __name__ == '__main__':
    sys.path.append(os.getcwd())  # Simulate running nosetests from the root.
    from tests import FunFactoryTests
    nose.main(addplugins=[FunFactoryTests()])
