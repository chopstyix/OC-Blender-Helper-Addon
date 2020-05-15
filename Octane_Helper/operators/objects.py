import bpy
import os
from math import pi
from .. icons import get_icon
from .. assets import load_objects, landscapes_dir, clouds_dir

def get_enum_landscape(self, context):
    items = []
    landscapes = []
    for fn in os.listdir(landscapes_dir):
        if (not fn.lower().endswith(".thumb.png")):
            landscapes.append(fn[:-4])
    for i, name in enumerate(landscapes):
        items.append((name, name, '', get_icon(name), i))
    return items

def update_enum_landscape(self, context):
    path = os.path.join(landscapes_dir, context.scene.oc_landscape + '.png')
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, rotation=(pi/2, 0, 0))
    bpy.ops.octane.assign_pattern(filepath=path)

def get_enum_cloud(self, context):
    items = []
    clouds = []
    for fn in os.listdir(clouds_dir):
        if (not fn.lower().endswith(".thumb.png")):
            clouds.append(fn[:-4])
    for i, name in enumerate(clouds):
        items.append((name, name, '', get_icon(name), i))
    return items

def update_enum_cloud(self, context):
    path = os.path.join(clouds_dir, context.scene.oc_cloud + '.png')
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, rotation=(pi/2, 0, 0))
    bpy.ops.octane.assign_pattern(filepath=path)