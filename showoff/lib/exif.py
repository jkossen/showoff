from flask import current_app
from PIL import ExifTags, Image
import os

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

# update_exif {{{
def update_exif(album, filename):
    exifdir = os.path.join(current_app.config['CACHE_DIR'], album, 'exif')
    exiffile = os.path.join(exifdir, os.path.basename(filename) + '.exif')
    if not os.path.exists(exifdir):
        os.mkdir(exifdir)
    img = Image.open(os.path.join(current_app.config['ALBUMS_DIR'], album, filename))
    if not hasattr(img, '_getexif'):
        return None
    exif = img._getexif()

    if exif == None:
        return

    ret = {}
    if exif:
        for tag, value in exif.items():
            decoded = ExifTags.TAGS.get(tag, tag)
            ret[decoded] = value
    f = open(exiffile, 'w')
    for key in supported_exiftags:
        if ret.has_key(key):
            f.write("%s|%s\n" % (key, ret[key]))
    f.close()
    return ret
# }}}

def get_exif(album, filename):
    exifdir = os.path.join(current_app.config['CACHE_DIR'], album, 'exif')
    exiffile = os.path.join(exifdir, os.path.basename(filename) + '.exif')

    exif = {}

    if os.path.exists(exiffile):
        f = open(exiffile)
        for line in f.readlines():
            line_arr = line.split('|')
            if len(line_arr) > 1:
                exif[line_arr[0]] = line_arr[1]
        f.close()
    else:
        exif = update_exif(album, filename)

    return exif

