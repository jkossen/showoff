===================================
Showoff - Webbased photo management
===================================
:Author: Jochem Kossen

Showoff is a webbased image gallery and photo directory management system,
written in Python_, utilizing Flask_ and for the interface a slightly modified
Galleriffic_, a JQuery_ plugin.

For a live demo of the viewer app, see http://jkossen.nl/showoff/public.html

Copyright and license
---------------------

:copyright: (c) 2010-2012 by Jochem Kossen <jochem@jkossen.nl>
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

* Non-destructive: Showoff does not change original files

* Image rotation based on exif data

* Image albums are just directories with image files, showoff will find and
  generate the required metadata for you.

* You can use the admin to select which photo's should be published in the
  "show" which is the publicly visible album

* Separate frontend and admin apps

* No database is used (everything is in flat-file or json files)

* Theme support (Jinja2 is used for templates)

Installation
------------

Requirements
~~~~~~~~~~~~
Showoff requires the following software:

* `Python`_ (developed with 2.5 provided with Debian Lenny)
* `Flask`_
* Flask-WTF
* py_bcrypt
* `Werkzeug`_
* `Jinja2`_
* PIL

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
.. _Galleriffic: http://www.twospy.com/galleriffic/
.. _JQuery: http://jquery.com/
.. _Werkzeug: http://werkzeug.pocoo.org
.. _Jinja2: http://jinja.pocoo.org
