import bpy.utils.previews as previews
import os

icons = None
icons_dir = os.path.dirname(__file__)

# Get the icon id
def get_icon(name):
    if name not in icons:
        return icons['OBJ_THUMB'].icon_id
    return icons[name].icon_id

# Register icons
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