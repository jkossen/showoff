#!/usr/bin/env python

"""
Imposter - Another weblog app
Copyright (c) 2010 by Jochem Kossen <jochem.kossen@gmail.com>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

   1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
   2. Redistributions in binary form must reproduce the above
   copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials provided
   with the distribution.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
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

This is the frontend application code for Imposter. It's only used for
viewing content, not manipulation.

"""

from flask import Flask, render_template, send_from_directory, abort, url_for, redirect
from werkzeug import cached_property

import os, re, Image
from ExifTags import TAGS

#---------------------------------------------------------------------------
# INITIALIZATION

app = Flask(__name__, static_path=None)
app.config.from_pyfile('config.py')
app.config.from_envvar('SPREAD_FRONTEND_CONFIG', silent=True)

supported_exiftags = [
    "ImageWidth",
    "ImageLength",
    "BitsPerSample",
    "Compression",
    "PhotometricInterpretation",
    "ImageDescription",
    "Make",
    "Model",
    "StripOffsets",
    "Orientation",
    "SamplesPerPixel",
    "RowsPerStrip",
    "StripByteConunts",
    "XResolution",
    "YResolution",
    "PlanarConfiguration",
    "ResolutionUnit",
    "TransferFunction",
    "Software",
    "DateTime",
    "Artist",
    "WhitePoint",
    "PrimaryChromaticities",
    "JpegIFOffset",
    "JpegIFByteCount",
    "YCbCrCoefficients",
    "YCbCrSubSampling",
    "YCbCrPositioning",
    "ReferenceBlackWhite",
    "RelatedImageFileFormat",
    "RelatedImageLength",
    "RelatedImageWidth",
    "CFARepeatPatternDim",
    "CFAPattern",
    "BatteryLevel",
    "Copyright",
    "ExposureTime",
    "FNumber",
    "ExifOffset",
    "InterColorProfile",
    "ExposureProgram",
    "SpectralSensitivity",
    "GPSInfo",
    "ISOSpeedRatings",
    "OECF",
    "Interlace",
    "TimeZoneOffset",
    "SelfTimerMode",
    "ExifVersion",
    "DateTimeOriginal",
    "DateTimeDigitized",
    "ComponentsConfiguration",
    "CompressedBitsPerPixel",
    "CompressedBitsPerPixel",
    "ShutterSpeedValue",
    "ApertureValue",
    "BrightnessValue",
    "ExposureBiasValue",
    "MaxApertureValue",
    "SubjectDistance",
    "MeteringMode",
    "LightSource",
    "Flash",
    "FocalLength",
    "FlashEnergy",
    "SpatialFrequencyResponse",
    "Noise",
    "ImageNumber",
    "SecurityClassification",
    "ImageHistory",
    "SubjectLocation",
    "ExposureIndex",
    "TIFF/EPStandardID",
    "UserComment",
    "SubsecTime",
    "SubsecTimeOriginal",
    "SubsecTimeDigitized",
    "FlashPixVersion",
    "ColorSpace",
    "ExifImageWidth",
    "ExifImageHeight",
    "RelatedSoundFile",
    "ExifInteroperabilityOffset",
    "FlashEnergy",
    "SpatialFrequencyResponse",
    "FocalPlaneXResolution",
    "FocalPlaneYResolution",
    "FocalPlaneResolutionUnit",
    "SubjectLocation",
    "ExposureIndex",
    "SensingMethod",
    "FileSource",
    "SceneType",
    "CFAPattern",
    ]

#
# CLASSES
class Paginator(object):
    def __init__(self, album, items, per_page, page, endpoint):
        self.album = album
        self.items = items
        self.per_page = per_page
        self.page = page
        self.endpoint = endpoint

        if (self.page > self.pages or self.page < 1):
            abort(404)

    @cached_property
    def count(self):
        return len(self.items)

    @cached_property
    def entries(self):
        offset = (self.page - 1) * self.per_page
        end = offset + self.per_page
        return self.items[offset:end]

    has_previous = property(lambda x: x.page > 1)
    has_next = property(lambda x: x.page < x.pages)
    previous = property(lambda x: url_for(x.endpoint, album=x.album, page=x.page - 1))
    next = property(lambda x: url_for(x.endpoint, album=x.album, page=x.page + 1))
    first = property(lambda x: url_for(x.endpoint, album=x.album, page=1))
    last = property(lambda x: url_for(x.endpoint, album=x.album, page=x.pages))
    pages = property(lambda x: max(0, x.count - 1) // x.per_page + 1)

#---------------------------------------------------------------------------
# SHORTCUT FUNCTION
def get_route(function):
    """Return complete route based on configuration and routes"""
    return '/%s%s' % (app.config['FRONTEND_PREFIX'],
                      app.config['FRONTEND_ROUTES'][function])

def themed(template):
    """Return path to template in configured theme"""
    return os.path.join('frontend', app.config['THEME'], template)

#---------------------------------------------------------------------------
# TEMPLATE FILTERS


#---------------------------------------------------------------------------
# FRONTEND VIEWS

@app.route(get_route('static_files'))
def static(filename):
    """Send static files such as style sheets, JavaScript, etc."""
    static_path = os.path.join(app.root_path, 'templates', 'frontend',
                               app.config['THEME'], 'static')
    return send_from_directory(static_path, filename)

def get_edit_or_original(album, filename):
    orig = app.config['ALBUMS'][album]
    edit = os.path.join(app.config['EDITS_DIR'], album)

    if os.path.exists(os.path.join(edit, filename)):
        return edit
    else:
        return orig

def clear_cache(album, filename, size):
    path_to_file = os.path.join(app.config['CACHE_DIR'], str(album), str(size), os.path.basename(filename))
    if os.path.exists(path_to_file):
        os.unlink(path_to_file)
        
def update_cache(album, filename, size):
    adir = os.path.join(app.config['CACHE_DIR'], album)
    if not os.path.exists(adir):
        os.mkdir(adir)
    tdir = os.path.join(adir, str(int(size)))
    if not os.path.exists(tdir):
        os.mkdir(tdir)

    img = Image.open(os.path.join(get_edit_or_original(album, filename), filename))
    img.thumbnail((size, size), Image.ANTIALIAS)
    img.save(os.path.join(tdir, os.path.basename(filename)), "JPEG")

def update_exif(album, filename):
    exifdir = os.path.join(app.config['CACHE_DIR'], album, 'exif')
    exiffile = os.path.join(exifdir, os.path.basename(filename) + '.exif')
    if not os.path.exists(exifdir):
        os.mkdir(exifdir)
    img = Image.open(os.path.join(app.config['ALBUMS'][album], filename))
    exif = img._getexif()
    ret = {}
    for tag, value in exif.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    f = open(exiffile, 'w')
    for key in supported_exiftags:
        if ret.has_key(key):
            f.write("%s|%s\n" % (key, ret[key]))
    f.close()

@app.route(get_route('show_image'))
def show_image(album, filename, size=None):
    """Send static files such as style sheets, JavaScript, etc."""
    if size is not None:
        adir = os.path.join(app.config['CACHE_DIR'], album)
        if not os.path.exists(adir):
            os.mkdir(adir)
        tdir = os.path.join(adir, str(int(size)))
        if not os.path.exists(os.path.join(tdir, os.path.basename(filename))):
            update_cache(album, filename, size)

        exifdir = os.path.join(app.config['CACHE_DIR'], album, 'exif')
        exiffile = os.path.join(exifdir, os.path.basename(filename) + '.exif')
        if not os.path.exists(exiffile):
            update_exif(album, filename)

        return send_from_directory(tdir, filename)
    else:
        return send_from_directory(get_edit_or_original(album, filename), filename)

@app.route(get_route('rotate_image'))
def rotate_image(album, filename):
    imgfile = os.path.join(get_edit_or_original(album, filename), filename)
    img = Image.open(imgfile)
    img = img.rotate(-90)
    efile = os.path.join(app.config['EDITS_DIR'], album, filename)
    if not os.path.exists(os.path.join(app.config['EDITS_DIR'], album)):
        os.mkdir(os.path.join(app.config['EDITS_DIR'], album))
    img.save(efile, "JPEG")
    for size in app.config['ALLOWED_SIZES']:
        if size != 'full':
            clear_cache(album, filename, size)
    return redirect(url_for('image_page', album=album, filename=filename))

@app.route(get_route('show_image_full'))
def show_image_full(album, filename):
    return show_image(album, filename)

def get_exif_table(exif):
    table = '<table>'
    for line in exif:
        table = table + '<tr><td>' + line.replace('|', '</td><td>') + '</td></tr>'
    table = table + '</table>'
    return table

@app.route(get_route('image_page'))
def image_page(album, filename):
    exifdir = os.path.join(app.config['CACHE_DIR'], album, 'exif')
    f = open(os.path.join(exifdir, filename + '.exif'))
    exif_array = f.readlines()
    f.close()
    
    return render_template(themed('image.html'), album=album, filename=filename, exif=get_exif_table(exif_array))

@app.route(get_route('list'))
def list(album, page):
    files = os.listdir(app.config['ALBUMS'][album])

    # only list .jpg files
    ext = re.compile(".jpg$", re.IGNORECASE)
    files = filter(ext.search, files)

    files.sort()
    p = Paginator(album, files, app.config['THUMBNAILS_PER_PAGE'], page, 'list')
    return render_template(themed('list.html'), album=album, files=p.entries, paginator=p)

@app.route(get_route('album'))
def show_album(album):
    """Render first page of album"""
    return list(album, 1)

@app.route(get_route('index'))
def show_index():
    """Render frontpage"""
    return render_template(themed('index.html'), albums=app.config['ALBUMS'])

#---------------------------------------------------------------------------
# MAIN RUN LOOP
if __name__ == '__main__':
    app.run(host=app.config['FRONTEND_HOST'], port=app.config['FRONTEND_PORT'])
