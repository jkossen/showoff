class Error(Exception):
    pass

class UnknownFileError(Error):
    pass

class UnsupportedSettingError(Error):
    pass

class NoSuchPageError(Error):
    pass

class UnsupportedImageSizeError(Error):
    pass
