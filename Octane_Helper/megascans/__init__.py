# ##### QUIXEL AB - Octane Megascans Module FOR BLENDER #####
#
# The Octane Megascans Module  module for Blender is an add-on that lets
# you instantly import assets with their shader setup with one click only.
#
# Because it relies on some of the latest 2.80 features, this module is currently
# only available for Blender 2.80 and forward.
#
# You are free to modify, add features or tweak this add-on as you see fit, and
# don't hesitate to send us some feedback if you've done something cool with it.
#
# ##### QUIXEL AB - Octane Megascans Module FOR BLENDER #####

import bpy
import threading
import os
import json
from bpy.app.handlers import persistent
from . threads import *
from . helpers import *
from .. operators.materials import create_material, assign_material_objs

globals()['Megascans_DataSet'] = None

# This stuff is for the Alembic support
globals()['MG_AlembicPath'] = []
globals()['MG_Material'] = []
globals()['MG_ImportComplete'] = False

disp_levels = {
    '2K': 'OCTANE_DISPLACEMENT_LEVEL_2048',
    '4K': 'OCTANE_DISPLACEMENT_LEVEL_4096',
    '8K': 'OCTANE_DISPLACEMENT_LEVEL_8192'
}

def init_import():
    if(bpy.context.scene.render.engine != 'octane'):
        print('[Octane Helper] Please activate the Octane engine in order to use the Octane Megascans Module')
        return None
    
    globals()['MG_AlembicPath'] = []
    globals()['MG_Material'] = []
    globals()['MG_ImportComplete'] = False
    
    json_array = json.loads(globals()['Megascans_DataSet'])

    result = []

    for json_data in json_array:
        # Asset
        name = json_data['name'].replace(" ", "_")
        aid = json_data['id']
        atype = json_data['type']
        path = json_data['path']
        category = json_data['category']
        categories = json_data['categories']
        tags = json_data['tags']
        meshes = [mesh for mesh in json_data['meshList']]
        components = [component for component in json_data['components'] if component['type'] in supported_textures]
        components.sort(key=component_sort)

        # Convert diffuse to albedo
        has_albedo = (len([component for component in json_data['components'] if component['type']=='albedo']) != 0)
        for component in components:
            if(component['type']=='diffuse' and not has_albedo):
                component['type'] = 'albedo'
        
        result.append({
            'name': name, 
            'id': aid, 
            'type': atype, 
            'path': path,
            'category': category,
            'categories': categories,
            'tags': tags,
            'meshes': meshes,
            'components': components
        })
    
    return result

def import_meshes(element):
    if(bpy.context.scene.render.engine != 'octane'):
        print('[Octane Helper] Please activate the Octane engine in order to use the Octane Megascans Module')
        return None
    
    meshes = element['meshes']

    objects = []
    for mesh in meshes:
        mesh_path = mesh['path']
        mesh_format = mesh['format']

        bpy.ops.object.select_all(action='DESELECT')

        if mesh_format.lower() == "fbx":
            bpy.ops.import_scene.fbx(filepath=mesh_path)
            # get selected objects
            objects += [ o for o in bpy.context.scene.objects if o.select_get() ]

        elif mesh_format.lower() == "obj":
            bpy.ops.import_scene.obj(filepath=mesh_path, use_split_objects = True, use_split_groups = True, global_clight_size = 1.0)
            # get selected objects
            objects += [ o for o in bpy.context.scene.objects if o.select_get() ]
    
    # Scatter, Plants
    if (is_in_element(['scatter', 'plants'], element) and len(objects)):
        group_into_empty(objects, element['name'])

    return objects

def import_material(element):
    if(bpy.context.scene.render.engine != 'octane'):
        print('[Octane Helper] Please activate the Octane engine in order to use the Octane Megascans Module')
        return None
    
    components = element['components']
    mat_name = element['name']

    prefs = bpy.context.preferences.addons['Octane_Helper'].preferences
    mat = create_material(bpy.context, 'MS_' + mat_name, 'OctaneUniversalMaterial')
    ntree = mat.node_tree
    nodes = ntree.nodes
    textures = [component['type'] for component in components]

    # Add image textures
    add_components_tex(ntree, element)

    # All to copied
    #if (is_in_element(['surface', 'atlas'], element)):
    bpy.types.Material.copied_mat = mat

    # Albedo and AO
    if('albedo' in textures):
        if('ao' in textures):
            multiplyNode = nodes.new('OctaneMultiplyTexture')
            multiplyNode.name = 'ao_multiply_albedo'
            multiplyNode.location = (-320, 300)
            ntree.links.new(nodes['ao'].outputs[0], nodes['ao_multiply_albedo'].inputs[0])
            ntree.links.new(nodes['albedo'].outputs[0], nodes['ao_multiply_albedo'].inputs[1])
            ntree.links.new(nodes['ao_multiply_albedo'].outputs[0], nodes['root'].inputs['Albedo'])
        else:
            ntree.links.new(nodes['albedo'].outputs[0], nodes['root'].inputs['Albedo'])
    
    # Specular
    if('specular' in textures):
        ntree.links.new(nodes['specular'].outputs[0], nodes['root'].inputs['Specular'])
    
    # Roughness
    if('roughness' in textures):
        ntree.links.new(nodes['roughness'].outputs[0], nodes['root'].inputs['Roughness'])
        nodes['roughness'].inputs['Gamma'].default_value = 1
    
    # Metalness
    #if(element['category'] == 'Metal'):
    #    nodes['root'].inputs['Metallic'].default_value = 1
    
    if('metalness' in textures):
        ntree.links.new(nodes['metalness'].outputs[0], nodes['root'].inputs['Metallic'])
        nodes['metalness'].inputs['Gamma'].default_value = 1
    
    # Displacement
    if('displacement' in textures):
        nodes['displacement'].inputs['Gamma'].default_value = 1
        if prefs.disp_type == 'TEXTURE':
            resolution = get_component(components, 'displacement')['resolution']
            dispNode = nodes.new('OctaneTextureDisplacement')
            dispNode.name = 'disp'
            dispNode.displacement_level = disp_levels[resolution]
            dispNode.displacement_surface = 'Follow smoothed normal'
            dispNode.inputs['Mid level'].default_value = 0.5
            dispNode.inputs['Height'].default_value = 0.1
        else:
            dispNode = nodes.new('OctaneVertexDisplacement')
            dispNode.name = 'disp'
            dispNode.inputs['Auto bump map'].default_value = True
            dispNode.inputs['Mid level'].default_value = 0.1
            dispNode.inputs['Height'].default_value = 0.1
            dispNode.inputs['Subdivision level'].default_value = prefs.disp_level_vertex
        dispNode.location = (-320, -680)

        ntree.links.new(nodes['displacement'].outputs[0], nodes['disp'].inputs['Texture'])
        ntree.links.new(nodes['disp'].outputs[0], nodes['root'].inputs['Displacement'])
    
    # Translucency
    if('translucency' in textures):
        scatterNode = nodes.new('OctaneScattering')
        scatterNode.name = 'translucency_scatter'
        scatterNode.inputs['Absorption'].default_value = (1, 1, 1)
        scatterNode.inputs['Invert absorption'].default_value = True
        scatterNode.location = (-320, -1000)
        ntree.links.new(nodes['translucency'].outputs[0], nodes['root'].inputs['Transmission'])
        ntree.links.new(nodes['translucency_scatter'].outputs[0], nodes['root'].inputs['Medium'])
    
    # Opacity
    if('opacity' in textures):
        ntree.links.new(nodes['opacity'].outputs[0], nodes['root'].inputs['Opacity'])

    # Normal
    if('normal' in textures):
        ntree.links.new(nodes['normal'].outputs[0], nodes['root'].inputs['Normal'])
        nodes['normal'].inputs['Gamma'].default_value = 1
    
    # Bump
    # ---
    
    # Fuzz
    # ---
    
    # Cavity
    # ---
    
    # Curvature
    # ---

    return mat

class OctaneMSLiveLink(bpy.types.Operator):
    bl_idname = 'octane.ms_livelink'
    bl_label = 'Octane Megascans Module'
    socketCount = 0

    def execute(self, context):
        try:
            globals()['Megascans_DataSet'] = None
            self.thread_ = threading.Thread(target=self.socketMonitor)
            self.thread_.start()
            bpy.app.timers.register(self.newDataMonitor)
            return {'FINISHED'}
        except Exception as e:
            print('[Octane Helper] Octane Megascans Module Error (OctaneMSLiveLink):', str(e))
            return {'FAILED'}

    def newDataMonitor(self):
        # Try to start the import process if there is a task every 1 second
        try:
            if globals()['Megascans_DataSet'] != None:
                # Start Import
                elements = init_import()
                if(elements):
                    for element in elements:
                        # Import meshes and material
                        objs = import_meshes(element)
                        mat = import_material(element)
                        assign_material_objs(objs, mat)
                        # Select objects
                        if(len(objs)==1):
                            bpy.context.view_layer.objects.active = objs[0]
                        elif(len(objs)>1):
                            for obj in objs:
                                obj.select_set(True)
                            bpy.context.view_layer.objects.active = objs[0]
                # Finish Import
                print('Imported an asset from Quixel Bridge')
                globals()['Megascans_DataSet'] = None
        except Exception as e:
            print('[Octane Helper] Octane Megascans Module Error (newDataMonitor):', str(e))
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
            print('[Octane Helper] Octane Megascans Module Error (socketMonitor):', str(e))
            return {'FAILED'}

    def importer(self, recv_data):
        try:
            globals()['Megascans_DataSet'] = recv_data
        except Exception as e:
            print('[Octane Helper] Octane Megascans Module Error starting blender module (importer). Error: ', str(e))
            return {'FAILED'}

@persistent
def load_ms_module(scene):
    try:
        bpy.ops.octane.ms_livelink()
    except Exception as e:
        print('[Octane Helper] Failed to start the Octane Megascans Module: ', str(e))

def register_megascans():
    if(is_official_here()):
        print('[Octane Helper] Failed to start the Octane Megascans Module: the port is used by the official Quixel add-on, please follow the instruction on wiki to remove it')
        return
    if(is_me_here()):
        return
    bpy.utils.register_class(OctaneMSLiveLink)
    bpy.app.handlers.load_post.append(load_ms_module)

def unregister_megascans():
    if(is_official_here()):
        return
    if(is_me_here()):
        return
    bpy.app.handlers.load_post.remove(load_ms_module)
    bpy.utils.unregister_class(OctaneMSLiveLink)
    if len(bpy.app.handlers.load_post) > 0:
        # Check if trying to register twice.
        if 'load_ms_module' in bpy.app.handlers.load_post[0].__name__.lower() or load_ms_module in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(load_ms_module)
