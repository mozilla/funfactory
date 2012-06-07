#!/usr/bin/bash
# This is a smoke test to check the installer from Jenkins CI.
rm -fr installer_test
./.tox/bin/py26/bin/funfactory --no-input --pkg installer_test
exit $?
