from PIL import ExifTags, Image
import os


class ExifManager(object):
    def __init__(self, image):
        self.image = image
        self.supported_exiftags = [
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
            "CFAPattern"
        ]

    def update(self):
        if not os.path.exists(self.image.exif_dir):
            os.mkdir(self.image.exif_dir)
        img = Image.open(self.image.orig_file)
        if not hasattr(img, '_getexif'):
            return None
        exif = img._getexif()

        if exif is None:
            return

        ret = {}
        if exif:
            for tag, value in exif.items():
                decoded = ExifTags.TAGS.get(tag, tag)
                try:
                    ret[decoded] = str(value).encode('utf-8')
                except:
                    pass

        with open(self.image.exif_file, 'w') as f:
            for key in self.supported_exiftags:
                if key in ret:
                    f.write("%s|%s\n" % (key, ret[key]))
        return ret

    def get_exif(self):
        exif = {}

        if os.path.exists(self.image.exif_file):
            with open(self.image.exif_file) as f:
                for line in f.readlines():
                    line_arr = line.split('|')
                    if len(line_arr) > 1:
                        exif[line_arr[0]] = line_arr[1]
        else:
            exif = self.update()

        return exif

    def get_exif_tag_value(self, exif, tag):
        for tag, value in exif.items():
            decoded = ExifTags.TAGS.get(tag, tag)
            if decoded == tag:
                return value
        return None

    def get_exif_datetime(self):
        img = Image.open(self.image.orig_file)
        if not hasattr(img, "_getexif"):
            return None
        exif = img._getexif()
        datetime = self.get_exif_tag_value(exif, 'DateTime')
        return datetime
