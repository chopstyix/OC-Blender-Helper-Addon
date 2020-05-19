import bpy
import os
from math import pi
from .. icons import get_icon
from .. assets import load_objects, landscapes_dir, clouds_dir

# Read a dir and load filenames with given extension to a list then return the list
def append_from_dir(dir, ext):
    items = []
    files = []
    for fn in os.listdir(landscapes_dir):
        if ((fn.lower().endswith(ext)) and (not fn.lower().endswith(".thumb.png"))):
            files.append(fn[:-len(ext)])
    for i, name in enumerate(files):
        items.append((name, name, name, get_icon(name), i))
    return items

def get_enum_landscape_plane(self, context):
    items = append_from_dir(landscapes_dir, '.png')
    return items

def get_enum_landscape_mesh(self, context):
    items = append_from_dir(landscapes_dir, '.blend')
    return items

def update_enum_landscape_plane(self, context):
    path = os.path.join(landscapes_dir, context.scene.oc_landscape_plane + '.png')
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, rotation=(pi/2, 0, 0))
    bpy.ops.octane.assign_pattern(filepath=path)

def update_enum_landscape_mesh(self, context):
    load_objects(context.scene.oc_landscape_mesh, 'landscapes')

# WIP
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