=======================
NIOS Control Zone Locks
=======================

| Version: 0.1.0
| Author: Chris Marrison
| Email: chris@infoblox.com

Description
-----------

Demo NIOS script to control the administrative control of authoritative
zones. Can be used to report on, lock or unlock either a specified zone, or
all zones.

Prerequisites
-------------

Python 3.7+


Installing Python
~~~~~~~~~~~~~~~~~

You can install the latest version of Python 3.x by downloading the appropriate
installer for your system from `python.org <https://python.org>`_.

.. note::

  If you are running MacOS Catalina (or later) Python 3 comes pre-installed.
  Previous versions only come with Python 2.x by default and you will therefore
  need to install Python 3 as above or via Homebrew, Ports, etc.

  By default the python command points to Python 2.x, you can check this using 
  the command::

    $ python -V

  To specifically run Python 3, use the command::

    $ python3


.. important::

  Mac users will need the xcode command line utilities installed to use pip3,
  etc. If you need to install these use the command::

    $ xcode-select --install

.. note::

  If you are installing Python on Windows, be sure to check the box to have 
  Python added to your PATH if the installer offers such an option 
  (it's normally off by default).


Modules
~~~~~~~

Non-standard modules:

    - rich (for pretty printing)

Complete list of modules::

  import logging
  import requests
  import argparse
  import configparser
  import time


Installation
------------

The simplest way to install and maintain the tools is to clone this 
repository::

    % git clone https://github.com/ccmarris/nios_manage_zone_locks


Alternative you can download as a Zip file.


Basic Configuration
-------------------

The script utilise a gm.ini file to specify the Grid Master, API version
and user/password credentials.


gm.ini
~~~~~~~

The *gm.ini* file is used by the scripts to define the details to connect to
to Grid Master. A sample inifile is provided and follows the following 
format::

  [NIOS]
  gm = '192.168.1.10'
  api_version = 'v2.12'
  valid_cert = 'false'
  user = 'admin'
  pass = 'infoblox'


You can use either an IP or hostname for the Grid Master. This inifile 
should be kept in a safe area of your filesystem. 

Use the --config/-c option to override the default ini file.


Usage
-----

The script support -h or --help on the command line to access the options 
available::

  % ./nios_manage_zone_locks.py --help 
  usage: nios_manage_zone_locks.py [-h] [-c CONFIG] [-z ZONE] [-l] [-u] [-d]

  Manage NIOS zone locks

  optional arguments:
    -h, --help            show this help message and exit
    -c CONFIG, --config CONFIG
                          Override ini file
    -z ZONE, --zone ZONE  Operate on specific zone
    -l, --lock            Lock zone(s)
    -u, --unlock          Unlock zone(s)
    -d, --debug           Enable debug messages



nios_manage_zone_locks
~~~~~~~~~~~~~~~~~~~~~~


Examples
--------

Report lock status of all zones::

  % ./nios_manage_zone_locks.py --config gm.ini 

Enable debug::

  % ./nios_manage_zone_locks.py --config gm.ini --debug

Report status of a specific zone::

  % ./nios_manage_zone_locks.py --config gm.ini --zone demozone.co.uk

Lock a specified zone::

  % ./nios_manage_zone_locks.py --config gm.ini --zone demozone.co.uk --lock

Unlock a specified zone::

  % ./nios_manage_zone_locks.py --config gm.ini --zone demozone.co.uk --unlock

Unlock all zones::

  % ./nios_manage_zone_locks.py --config gm.ini --unlock


License
-------

This project is licensed under the 2-Clause BSD License
- please see LICENSE file for details.


Aknowledgements
---------------

Thanks to Ricky Ortiz for the requirement and initial testing.