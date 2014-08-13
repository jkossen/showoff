===================================
Showoff - Webbased photo management
===================================
:Author: Jochem Kossen

Showoff is a webbased photo album management system explicitly aimed at simple needs.

Showoff was written in Python_, utilizing Flask_. The frontend uses Bootstrap_,
jQuery_ and Swipebox_.

Showoff is separated into an admin app and a frontend app which can run
indepentently in different environments.

Copyright and license
---------------------

:copyright: (c) 2010-2014 by Jochem Kossen <jochem@jkossen.nl>
:license: two-clause BSD

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

   1. Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Showoff features and lack thereof
----------------------------------

* Non-destructive: Showoff does not change original files. All modifications
  are done on copies in the cache

* Image rotation based on exif data

* Image albums are just directories with image files, showoff will find and
  generate the required metadata for you.

* You can use the admin to select which photo's should be published in the
  "show" which is the publicly visible album

* You can set albums to require authentication for viewing, and add user
  accounts with view rights per album

* Separate frontend and admin apps

* No database is used (everything is in flat-file and json files)

* Theme support (Jinja2 is used for templates)

Installation
------------

Requirements
~~~~~~~~~~~~
Showoff requires the following software:

* `Python`_
* `Flask`_
* `Flask-WTF`_
* `py-bcrypt`_
* `Werkzeug`_
* `Jinja2`_
* `Pillow`_

Showoff comes with a setup.py installation script which uses setuptools.  The
following command will install showoff and its dependencies:

::

    $ python setup.py install

You can also use pip to install the dependencies, but then you need to register
the showoff installation manually (add the path to the showoff parent dir to a
file called showoff.pth inside your site-packages directory):

::

    $ pip install -r requirements.txt


Installation Instructions
~~~~~~~~~~~~~~~~~~~~~~~~~
* Install the software listed under `Requirements`_
* Adjust the configuration in config.py
* Make sure the CACHE_DIR is writable by both the admin and viewer apps
* Make sure the EDITS_DIR and SHOWS_DIR are readable by the viewer app and
  readable AND writable by the admin app

I recommend using a combination of uwsgi and nginx. See the examples dir for
relevant wsgi files.

Check http://flask.pocoo.org/docs/deploying/ for more information
concerning deployment.

.. _Python: http://www.python.org
.. _Flask: http://flask.pocoo.org
.. _Flask-WTF: https://flask-wtf.readthedocs.org/en/latest/
.. _Pillow: https://pillow.readthedocs.org/en/latest/
.. _py-bcrypt: http://www.mindrot.org/projects/py-bcrypt/
.. _jQuery: http://jquery.com/
.. _Bootstrap: http://getbootstrap.com
.. _Swipebox: http://brutaldesign.github.io/swipebox/
.. _Werkzeug: http://werkzeug.pocoo.org
.. _Jinja2: http://jinja.pocoo.org
