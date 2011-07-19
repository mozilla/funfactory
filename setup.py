import os

extra_setup = {}
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
else:
    extra_setup.update(dict(packages=find_packages(exclude=['ez_setup']),
                            install_requires=[]))

setup(
    name='funfactory',
    version='1.0',
    description="Mozilla's Django app skeleton.",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       'README.rst')).read(),
    author='Kumar McMillan and contributors',
    author_email='',
    license="Mozilla License",
    url='http://farmdev.com/projects/fudge/',
    include_package_data=True,
    classifiers = [
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        ],
    **extra_setup
    )
