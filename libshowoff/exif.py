from ExifTags import TAGS
import os, Image

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

