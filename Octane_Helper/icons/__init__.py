import bpy.utils.previews as previews
import os

icons = None
icons_dir = os.path.dirname(__file__)
mountains_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'mountains')

def get_icon(name):
    return icons[name].icon_id

def register_icons():
    global icons
    icons = previews.new()
    for fn in os.listdir(icons_dir):
        if fn.endswith('.png'):
            name = fn[:-4]
            path = os.path.join(icons_dir, fn)
            icons.load(name, path, 'IMAGE')
    for fn in os.listdir(mountains_dir):
        if fn.endswith('.thumb.png'):
            name = fn[:-10]
            path = os.path.join(mountains_dir, fn)
            icons.load(name, path, 'IMAGE')

def unregister_icons():
    previews.remove(icons)