from showoff.lib import CacheManager
from PIL import ExifTags, Image
import os


class ImageModifier(object):
    def __init__(self, image):
        self.image = image
        self.cache = CacheManager(image)

    def rotate(self, steps=1):
        if steps < 1:
            steps = 1
        if steps > 3:
            steps = 3

        img = Image.open(self.image.get_fullsize_path())
        img = img.rotate(steps * -90)

        if not os.path.exists(self.image.edit_dir):
            os.mkdir(self.image.edit_dir)

        img.save(self.image.edit_file, "JPEG")

        self.cache.clear()

    def rotate_exif(self):
        orientation_steps = {3: 2, 6: 1, 8: 3}
        if not self.image.is_edited():
            img = Image.open(self.image.orig_file)
            if not hasattr(img, "_getexif"):
                return
            exif = img._getexif()
            ret = {}
            for tag, value in exif.items():
                decoded = ExifTags.TAGS.get(tag, tag)
                ret[decoded] = value
            if 'Orientation' in ret:
                orientation = int(ret['Orientation'])
                if orientation in orientation_steps:
                    self.rotate(orientation_steps[orientation])
