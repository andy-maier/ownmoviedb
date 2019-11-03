#!/usr/bin/env python
# -----------------------------------------------------------------------------
# Copyright 2012-2017 Andreas Maier. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------

"""
Python setup script for ownmoviedb project.
"""

import os
import re
import setuptools


def get_version(version_file):
    """
    Execute the specified version file and return the value of the __version__
    global variable that is set in the version file.

    Note: Make sure the version file does not depend on any packages in the
    requirements list of this package (otherwise it cannot be executed in
    a fresh Python environment).
    """
    with open(version_file, 'r') as fp:
        version_source = fp.read()
    globals = {}
    exec(version_source, globals)
    return globals['__version__']


def get_requirements(requirements_file):
    """
    Parse the specified requirements file and return a list of its non-empty,
    non-comment lines. The returned lines are without any trailing newline
    characters.
    """
    with open(requirements_file, 'r') as fp:
        lines = fp.readlines()
    reqs = []
    for line in lines:
        line = line.strip('\n')
        if not line.startswith('#') and line != '':
            reqs.append(line)
    return reqs


def read_file(file):
    """
    Read the specified file and return its content as one string.
    """
    with open(file, 'r') as fp:
        content = fp.read()
    return content

pypi_package_name = 'ownmoviedb'
python_package_name = 'ownmoviedb'

requirements = get_requirements('requirements.txt')
install_requires = [req for req in requirements
                    if req and not re.match(r'[^:]+://', req)]
dependency_links = [req for req in requirements
                    if req and re.match(r'[^:]+://', req)]
package_version = get_version(os.path.join(python_package_name, 'version.py'))

# Docs on setup():
# * https://docs.python.org/2.7/distutils/apiref.html?
#   highlight=setup#distutils.core.setup
# * https://setuptools.readthedocs.io/en/latest/setuptools.html#
#   new-and-changed-setup-keywords
setuptools.setup(
    name=pypi_package_name,
    version=package_version,
    packages=[
        python_package_name,
    ],
    include_package_data=True,  # as specified in MANIFEST.in
    scripts=[
        'ownmoviedb_check.py',
        'ownmoviedb_check.bat',
        'ownmoviedb_gen_movielist.py',
        'ownmoviedb_gen_movielist.bat',
        'ownmoviedb_gen_mymdb_missing.py',
        'ownmoviedb_gen_mymdb_missing.bat',
        'ownmoviedb_import_movies.py',
        'ownmoviedb_import_movies.bat',
        'ownmoviedb_link_movies.py',
        'ownmoviedb_link_movies.bat',
        'ownmoviedb_scan_files.py',
        'ownmoviedb_scan_files.bat',
        'ownmoviedb_tvbrowser_moviecheck.py',
        'ownmoviedb_tvbrowser_moviecheck.bat',
    ],
    install_requires=install_requires,
    dependency_links=dependency_links,

    description="Python utilities for maintaining my own movie database",
    long_description=read_file('README.rst'),
    license="Apache License, Version 2.0",
    author='Andreas Maier',
    author_email='andreas.r.maier@gmx.de',
    maintainer='Andreas Maier',
    maintainer_email='andreas.r.maier@gmx.de',
    url='https://github.com/andy-maier/ownmoviedb',
    project_urls={
        'Bug Tracker': 'https://github.com/andy-maier/ownmoviedb/issues',
        'Documentation': 'https://github.com/andy-maier/ownmoviedb',
        'Source Code': 'https://github.com/andy-maier/ownmoviedb',
    },

    options={'bdist_wheel': {'universal': True}},
    zip_safe=True,  # This package can safely be installed from a zip file
    platforms='any',

    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
