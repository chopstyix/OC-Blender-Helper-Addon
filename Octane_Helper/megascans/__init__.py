# ##### QUIXEL AB - MEGASCANS Module FOR BLENDER #####
#
# The Megascans Module  module for Blender is an add-on that lets
# you instantly import assets with their shader setup with one click only.
#
# Because it relies on some of the latest 2.80 features, this module is currently
# only available for Blender 2.80 and forward.
#
# You are free to modify, add features or tweak this add-on as you see fit, and
# don't hesitate to send us some feedback if you've done something cool with it.
#
# ##### QUIXEL AB - MEGASCANS Module FOR BLENDER #####

import bpy
import threading
import os
import json
from bpy.app.handlers import persistent
from . threads import *

globals()['Megascans_DataSet'] = None

# This stuff is for the Alembic support
globals()['MG_AlembicPath'] = []
globals()['MG_Material'] = []
globals()['MG_ImportComplete'] = False

# OctaneMSImportProcess is the main asset import class.
# This class is invoked whenever a new asset is set from Bridge.

def display_view3d():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                override = {'window': window, 'screen': screen, 'area': area}
                return override
    return {}

def init_import():
    globals()['MG_AlembicPath'] = []
    globals()['MG_Material'] = []
    globals()['MG_ImportComplete'] = False
    
    json_array = json.loads(globals()['Megascans_DataSet'])

    result = []

    for json_data in json_array:
        # Asset
        asset_name = json_data['name']
        asset_id = json_data['id']
        asset_type = json_data['type']
        asset_path = json_data['path']
        meshes = [mesh for mesh in json_data['meshList']]
        components = [component for component in json_data['components']]
        
        # Process components
        has_albedo = (len([component for component in json_data['components'] if component['type']=='albedo']) != 0)
        for component in components:
            # Convert diffuse to albedo
            if(component['type']=='diffuse' and not has_albedo):
                component['type'] = 'albedo'
        
        result.append({
            'asset_name': asset_name, 
            'asset_id': asset_id, 
            'asset_type': asset_type, 
            'asset_path': asset_path
            'meshes': meshes,
            'components': components
        })
    
    return result

def import_meshes(meshes):
    objects = []
    for mesh in meshes:
        mesh_path = obj['path']
        mesh_format = obj['format']

        if mesh_format.lower() == "fbx":
            bpy.ops.import_scene.fbx(filepath=mesh_path)
            # get selected objects
            obj_objects = [ o for o in bpy.context.scene.objects if o.select_get() ]
            objects += obj_objects

        elif mesh_format.lower() == "obj":
            bpy.ops.import_scene.obj(filepath=mesh_path, use_split_objects = True, use_split_groups = True, global_clight_size = 1.0)
            # get selected objects
            obj_objects = [ o for o in bpy.context.scene.objects if o.select_get() ]
            objects += obj_objects
    
    return objects

class OctaneMSLiveLink(bpy.types.Operator):
    bl_idname = 'octane.ms_livelink'
    bl_label = 'Megascans Module'
    socketCount = 0

    def execute(self, context):
        try:
            globals()['Megascans_DataSet'] = None
            self.thread_ = threading.Thread(target=self.socketMonitor)
            self.thread_.start()
            bpy.app.timers.register(self.newDataMonitor)
            return {'FINISHED'}
        except Exception as e:
            print('Megascans Module Error starting blender module. Error: ', str(e))
            return {'FAILED'}

    def newDataMonitor(self):
        # Try to start the import process if there is a task every 1 second
        try:
            if globals()['Megascans_DataSet'] != None:
                # Call these from another operator
                result = init_import()
                objects = import_meshes(result['meshes'])

                globals()['Megascans_DataSet'] = None
        except Exception as e:
            print(
                'Megascans Module Error starting blender module (newDataMonitor). Error: ', str(e))
            return {'FAILED'}
        return 1.0

    def socketMonitor(self):
        try:
            # Making a thread object
            threadedServer = ms_Init(self.importer)
            # Start the newly created thread.
            threadedServer.start()
            # Making a thread object
            thread_checker_ = thread_checker()
            # Start the newly created thread.
            thread_checker_.start()
        except Exception as e:
            print(
                'Megascans Module Error starting blender module (socketMonitor). Error: ', str(e))
            return {'FAILED'}

    def importer(self, recv_data):
        try:
            globals()['Megascans_DataSet'] = recv_data
        except Exception as e:
            print(
                'Megascans Module Error starting blender module (importer). Error: ', str(e))
            return {'FAILED'}

@persistent
def load_ms_module(scene):
    try:
        bpy.ops.octane.ms_livelink()
    except Exception as e:
        print('Failed to start the Megascans module: ', str(e))


def register_megascans():
    if len(bpy.app.handlers.load_post) > 0:
        # Check if trying to register twice.
        if 'load_ms_module' in bpy.app.handlers.load_post[0].__name__.lower() or load_ms_module in bpy.app.handlers.load_post:
            return
    bpy.utils.register_class(OctaneMSLiveLink)
    bpy.app.handlers.load_post.append(load_ms_module)


def unregister_megascans():
    bpy.app.handlers.load_post.remove(load_ms_module)
    bpy.utils.unregister_class(OctaneMSLiveLink)
    if len(bpy.app.handlers.load_post) > 0:
        # Check if trying to register twice.
        if 'load_ms_module' in bpy.app.handlers.load_post[0].__name__.lower() or load_ms_module in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(load_ms_module)
