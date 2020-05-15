import bpy
import os
from .. icons import get_icon
from .. assets import load_objects, mountains_dir

def get_enum_mountain(self, context):
    items = []
    mountains = []
    for fn in os.listdir(mountains_dir):
        if (not fn.lower().endswith(".thumb.png")):
            mountains.append(fn[:-4])
    for i, name in enumerate(mountains):
        items.append((name, name, '', get_icon(name), i))
    return items

def update_enum_mountain(self, context):
    path = os.path.join(mountains_dir, context.scene.oc_mountain + '.png')
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False)
    bpy.ops.octane.assign_pattern(filepath=path)