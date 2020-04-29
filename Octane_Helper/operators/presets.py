
import bpy
from bpy.types import Operator

def refresh_presets_list(context):
    pass

# Classes
class OctanePresetsManager(Operator):
    bl_label = 'Presets manager'
    bl_idname = 'octane.presets_manager'
    bl_options = {'REGISTER'}

    def draw(self, context):
        pass
    
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        refresh_presets_list(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

'''
def get_enum_env_presets(self, context):
    # Called at any time
    result = [
        ('None', 'None', '')
    ]
    presets = os.path.join(bpy.utils.preset_paths('octane')[0], 'environments')
    if not os.path.isdir(presets):
        os.makedirs(presets)
    files = os.listdir(presets)
    if(len(files)==0):
        return [('None', 'None', '')]
    [result.append((file[:-6], file[:-6], '')) for file in files]
    return result


def update_enum_env_presets(self, context):
    # Called when switching presets
    if(self.preset != context.scene.selected_env_preset):
        context.scene.selected_env_preset = self.preset

    if(self.preset!='None'):
        prev_worlds = [world.name for world in bpy.data.worlds]
        presets = os.path.join(bpy.utils.preset_paths('octane')[0], 'environments')
        filepath = os.path.join(presets, self.preset+'.blend')
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.worlds = data_from.worlds
        curr_worlds = [world.name for world in bpy.data.worlds]
        context.scene.world = bpy.data.worlds[list(set(curr_worlds)-set(prev_worlds))[0]]
        refresh_worlds_list(context)
'''

# Classes
'''
class OctaneAddEnvironmentPreset(Operator):
    bl_label = 'Add an Environement Preset'
    bl_idname = 'octane.add_env_preset'

    save_name: StringProperty(name='Name', default='')
    pack_images: BoolProperty(name='Pack images', default=False, description='This option may take long time to process. Turn on only when you need to share presets across computers')

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, 'save_name')
        col = layout.column(align=True)
        col.prop(self, 'pack_images')

    def execute(self, context):
        # Create a Blend file
        if(self.save_name==''): 
            self.report({'WARNING'}, 'The name should not be empty')
            return {'CANCELLED'}
        if(self.save_name=='None'): 
            self.report({'WARNING'}, 'The name is invalid')
            return {'CANCELLED'}

        presets_dir = os.path.join(bpy.utils.preset_paths('octane')[0], 'environments')
        files = os.listdir(presets_dir)
        if(len([file for file in files if (file[:-6]==self.save_name)])):
            self.report({'WARNING'}, 'The name has beed used, try another one')
            return {'CANCELLED'}
        save_file = os.path.join(presets_dir, self.save_name + '.blend')

        # Save required data to the file
        # For iterable object, use '*items' instead if 'items'
        data_blocks = {
            bpy.context.scene.world
        }
        nodes = bpy.context.scene.world.node_tree.nodes
        if(self.pack_images):
            [node.image.pack() for node in nodes if (node.bl_idname in ['ShaderNodeOctImageTex', 'ShaderNodeOctImageTileTex', 'ShaderNodeOctFloatImageTex', 'ShaderNodeOctAlphaImageTex'] and node.image!=None)]   
        bpy.data.libraries.write(save_file, data_blocks, compress=True)
        if(self.pack_images):
            [node.image.unpack() for node in nodes if (node.bl_idname in ['ShaderNodeOctImageTex', 'ShaderNodeOctImageTileTex', 'ShaderNodeOctFloatImageTex', 'ShaderNodeOctAlphaImageTex'] and node.image!=None)]

        context.scene.selected_env_preset = self.save_name
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneRemoveEnvironmentPreset(Operator):
    bl_label = 'Remove an Environement Preset'
    bl_idname = 'octane.remove_env_preset'

    preset_name: StringProperty(default='')

    def execute(self, context):
        if(self.preset_name!='None' and self.preset_name!=None):
            presets_dir = os.path.join(bpy.utils.preset_paths('octane')[0], 'environments')
            os.remove(os.path.join(presets_dir, self.preset_name + '.blend'))
            context.scene.selected_env_preset = 'None'
        return {'FINISHED'}
'''