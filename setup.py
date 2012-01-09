import os
import re

from setuptools import setup, find_packages


version = None
for line in open('./funfactory/__init__.py'):
    m = re.search('__version__\s*=\s*(.*)', line)
    if m:
        version = m.group(1).strip()[1:-1]  # quotes
        break
assert version


setup(
    name='funfactory',
    version=version,
    description="Mozilla's Django app skeleton.",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       'README.rst')).read(),
    author='Kumar McMillan and contributors',
    author_email='',
    license="BSD License",
    url='https://github.com/mozilla/funfactory',
    include_package_data=True,
    classifiers = [
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        ],
    packages=find_packages(exclude=['tests']),
    entry_points="""
    [console_scripts]
    funfactory = funfactory.cmd:main
    """,
    install_requires=[])
