from flask import current_app
import os, Image

def is_edited(album, filename):
    edit = os.path.join(current_app.config['EDITS_DIR'], album)

    if os.path.exists(os.path.join(edit, filename)):
        return True
    else:
        return False

def get_edit_or_original(album, filename):
    edit = os.path.join(current_app.config['EDITS_DIR'], album)
    orig = os.path.join(current_app.config['ALBUMS_DIR'], album)

    if is_edited(album, filename):
        return edit
    else:
        return orig

def rotate_image(album, filename, steps=1):
    if steps < 1:
        steps = 1
    if steps > 3:
        steps = 3

    imgfile = os.path.join(get_edit_or_original(album, filename), filename)
    img = Image.open(imgfile)
    img = img.rotate(steps * -90)
    efile = os.path.join(current_app.config['EDITS_DIR'], album, filename)
    if not os.path.exists(os.path.join(current_app.config['EDITS_DIR'], album)):
        os.mkdir(os.path.join(current_app.config['EDITS_DIR'], album))
    img.save(efile, "JPEG")
