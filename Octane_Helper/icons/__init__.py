import bpy.utils.previews as previews
import os

icons = None
icons_dir = os.path.dirname(__file__)

def load_asset_dir(dir):
    for fn in os.listdir(dir):
        if fn.endswith('.thumb.png'):
            name = fn[:-10]
            path = os.path.join(dir, fn)
            icons.load(name, path, 'IMAGE')

def get_icon(name):
    if name not in icons:
        return icons['OBJ_THUMB'].icon_id
    return icons[name].icon_id

def register_icons():
    global icons
    icons = previews.new()
    for fn in os.listdir(icons_dir):
        if fn.endswith('.png'):
            name = fn[:-4]
            path = os.path.join(icons_dir, fn)
            icons.load(name, path, 'IMAGE')

def unregister_icons():
    previews.remove(icons)