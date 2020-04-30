import bpy 
import os

def load_objects(name):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), name + '.blend')
    with bpy.data.libraries.load(path) as (data_from, data_to):
        data_to.objects = data_from.objects
        bpy.ops.wm.append(directory=os.path.join(path, 'Object'), files=[{'name': name} for name in data_to.objects])
        return bpy.context.selected_objects

def save_objects(name, objects):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), name + '.blend')
    data_blocks = {
        *objects
    }
    bpy.data.libraries.write(path, data_blocks, compress=True)



'''
def save_preset(name, presets):
    path = os.path.join(bpy.utils.preset_paths('octane')[0], 'presets', name + '.blend')
    data_blocks = {}
    if 'Kernel' in presets:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        bpy.context.active_object.name = 'OC_Preset_Kernel'
        data_blocks.add(bpy.context.scene.oct_view_cam)
        data_blocks.add(bpy.context.active_object)
    if 'Environment' in presets:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        bpy.context.active_object.name = 'OC_Preset_Environment'
        data_blocks.add(bpy.context.scene.world)
        data_blocks.add(bpy.context.active_object)
    if 'Imager' in presets:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        bpy.context.active_object.name = 'OC_Preset_Imager'
        data_blocks.add(bpy.context.scene)
        data_blocks.add(bpy.context.active_object)
    bpy.data.libraries.write(path, data_blocks, compress=True)
'''