import os

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

