#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Gaël Lambert (gaelL) <gael.lambert@netwiki.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup


if __name__ == '__main__':

    setup(name='numeter-teeworlds-module',
          version='0.0.0.2',
          description='Numeter Teeworlds Poller module',
          long_description="""A Teeworlds module for Numeter poller. This module\
          use logtail and make players statistics with the teeworlds server log.
          Documentation is available here: https://github.com/shaftmx/numeter-teeworlds-module""",
          author='Gaël Lambert (gaelL)',
          author_email='gael@gael-lambert.org',
          maintainer='Gaël Lambert (gaelL)',
          maintainer_email='gael@gael-lambert.org',
          keywords=['numeter','graphing','poller','teeworlds'],
          url='https://github.com/shaftmx/numeter-teeworlds-module',
          license='GNU Affero General Public License v3',
          packages = [''],
          package_data={'': ['teeworldsModule.py']},
          classifiers=[
              'Development Status :: 4 - Beta',
              'Environment :: Console',
              'Intended Audience :: Advanced End Users',
              'Intended Audience :: System Administrators',
              'License :: OSI Approved :: GNU Affero General Public License v3',
              'Operating System :: POSIX',
              'Programming Language :: Python',
              'Topic :: System :: Monitoring'
          ],
         )
