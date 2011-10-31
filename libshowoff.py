# -*- coding: utf-8 -*-
from flask import json, url_for, abort
from werkzeug import cached_property
from ExifTags import TAGS
import os, Image

# LICENSE {{{
"""
Showoff - Webbased photo album software

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
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR#{{{# }}}
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

This is a library with generic code for showoff.

"""
# }}}

# VARIABLES {{{
# supported_exiftags {{{
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
# }}}
# }}}

# HELPER FUNCTIONS {{{
# get_exif_datetime {{{
def get_exif_datetime(app, album, filename):
    img = Image.open(os.path.join(app.config['ALBUMS_DIR'], album, filename))
    exif = img._getexif()
    ret = {}

    for tag, value in exif.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value

    if ret.has_key('DateTime'):
        return ret['DateTime']
    else:
        return '1970:01:01 00:00:00'
# }}}

# clear_cache {{{
def clear_cache(app, album, filename, size):
    path_to_file = os.path.join(app.config['CACHE_DIR'], str(album), str(size), os.path.basename(filename))
    if os.path.exists(path_to_file):
        os.unlink(path_to_file)
# }}}

# update_cache {{{
def update_cache(app, album, filename, size):
    adir = os.path.join(app.config['CACHE_DIR'], album)
    if not os.path.exists(adir):
        os.mkdir(adir)
    tdir = os.path.join(adir, str(int(size)))
    if not os.path.exists(tdir):
        os.mkdir(tdir)

    img = Image.open(os.path.join(get_edit_or_original(app, album, filename), filename))
    img.thumbnail((size, size), Image.ANTIALIAS)
    img.save(os.path.join(tdir, os.path.basename(filename)), "JPEG")
# }}}

# update_exif {{{
def update_exif(app, album, filename):
    exifdir = os.path.join(app.config['CACHE_DIR'], album, 'exif')
    exiffile = os.path.join(exifdir, os.path.basename(filename) + '.exif')
    if not os.path.exists(exifdir):
        os.mkdir(exifdir)
    img = Image.open(os.path.join(app.config['ALBUMS_DIR'], album, filename))
    exif = img._getexif()

    if exif == None:
        return

    ret = {}
    for tag, value in exif.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    f = open(exiffile, 'w')
    for key in supported_exiftags:
        if ret.has_key(key):
            f.write("%s|%s\n" % (key, ret[key]))
    f.close()
# }}}

def get_exif(app, album, filename):
    exifdir = os.path.join(app.config['CACHE_DIR'], album, 'exif')
    exiffile = os.path.join(exifdir, os.path.basename(filename) + '.exif')

    exif = {}

    if os.path.exists(exiffile):
        f = open(exiffile)
        for line in f.readline():
            exif[line.split('|')[0]] = line.split('|')[1]
        f.close()

    return exif

def is_edited(app, album, filename):
    edit = os.path.join(app.config['EDITS_DIR'], album)

    if os.path.exists(os.path.join(edit, filename)):
        return True
    else:
        return False

# get_edit_or_original {{{
def get_edit_or_original(app, album, filename):
    edit = os.path.join(app.config['EDITS_DIR'], album)
    orig = os.path.join(app.config['ALBUMS_DIR'], album)

    if is_edited(app, album, filename):
        return edit
    else:
        return orig
# }}}

# }}}

# CLASSES {{{
# Show class {{{
class Show(object):
    """A Show represents a public album for the admin"""
    def __init__(self, app, album):
        super(Show, self).__init__()
        self.app = app
        self.album = album
        self.show_dir = os.path.join(app.config['SHOWS_DIR'], album)
        self.show_file = os.path.join(self.show_dir, 'show.json')
        self.data = {'files': []}

        self.load()

    def nr_of_items(self):
        return len(self.data['files'])

    def is_enabled(self):
        return self.nr_of_items() > 0

    def add_image(self, filename):
        if filename not in self.data['files']:
            self.data['files'].append(filename)
            return self.save()
        return True

    def remove_image(self, filename):
        if filename in self.data['files']:
            self.data['files'].remove(filename)
            return self.save()
        return True

    def load(self):
        if os.path.exists(self.show_file):
            fp = open(self.show_file, 'r')
            self.data = json.load(fp)

    def sort_by_exif_datetime(self):
        filenames = []
        for filename in self.data['files']:
            datetime = get_exif_datetime(self.app, self.album, filename)
            filenames.append((datetime, filename))
        self.data['files'] = [v for (k, v) in sorted(filenames)]
        return self.save()

    def save(self):
        try:
            if not os.path.exists(self.show_dir):
                os.mkdir(self.show_dir)
            fp = open(self.show_file, 'w')
            js = json.dumps(self.data)
            fp.write(js)
            fp.close()
            return True
        except:
            return False
# }}}

# Paginator class {{{
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
# }}}
# }}}
