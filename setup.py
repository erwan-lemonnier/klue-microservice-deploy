from setuptools import setup
from os import path
import sys
import os
from glob import glob

version = None

if sys.argv[-2] == '--version' and 'sdist' in sys.argv:
    version = sys.argv[-1]
    sys.argv.pop()
    sys.argv.pop()

if 'sdist' in sys.argv and not version:
    raise Exception("Please set a version with --version x.y.z")

if not version:
    if 'sdist' in sys.argv:
        raise Exception("Please set a version with --version x.y.z")
    else:
        path_pkg_info = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'PKG-INFO')
        if os.path.isfile(path_pkg_info):
            with open(path_pkg_info, 'r')as f:
                for l in f.readlines():
                    if 'Version' in l:
                        _, version = l.split(' ')
        else:
            print("WARNING: cannot set version in custom setup.py")

if version:
    version = version.strip()
print("version: %s" % version)

# read the contents of the README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pymacaron-aws',
    version=version,
    url='https://github.com/pymacaron/pymacaron-aws',
    license='BSD',
    author='Erwan Lemonnier',
    author_email='erwan@lemonnier.se',
    description='Pymacaron deployment pipeline towards Amazon Beanstalk',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'awsebcli>=3.12.1',
        'awscli',
    ],
    tests_require=[
        'awsebcli>=3.12.1',
        'awscli',
        'nose',
        'mock',
        'pep8'
    ],
    test_suite='nose.collector',
    packages=['pymacaron_deploy_configs'],
    package_data={'pymacaron_deploy_configs': ['*.template', '*.config']},
    scripts=glob("bin/*"),
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
