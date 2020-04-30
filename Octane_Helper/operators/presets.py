'''
import bpy
from bpy.types import Operator
from bpy.props import StringProperty
import os

path = os.path.join(bpy.utils.preset_paths('octane')[0], 'presets')

def refresh_presets_list(context, active_last=False, active_default=False):
    context.scene.oc_presets.clear()

    if not os.path.isdir(path):
        os.makedirs(path)
    presets = ['Default'] + [path[:-6] for path in os.listdir(path)]

    for preset in presets:
        p = context.scene.oc_presets.add()
        p.name = preset
    
    if(active_last):
        context.scene.oc_presets_index = len(context.scene.oc_presets) - 1
    elif(active_default):
        context.scene.oc_presets_index = 0

def load_preset_kernel(context, name):
    pass

def load_preset_environment(context, name):
    prev_worlds = [world.name for world in bpy.data.worlds]
    path = os.path.join(bpy.utils.preset_paths('octane')[0], 'presets', name + '.blend')
    with bpy.data.libraries.load(path) as (data_from, data_to):
        data_to.worlds = data_from.worlds
    curr_worlds = [world.name for world in bpy.data.worlds]
    context.scene.world = bpy.data.worlds[list(set(curr_worlds)-set(prev_worlds))[0]]

def load_preset_imager(context, name):
    pass

# Classes
class OctanePresetsManager(Operator):
    bl_label = 'Presets manager'
    bl_idname = 'octane.presets_manager'
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.template_list('OCTANE_UL_preset_list', '', context.scene, 'oc_presets', context.scene, 'oc_presets_index')
        sub = row.column(align=True)
        sub.operator(OctaneAddPreset.bl_idname, text='', icon='ADD')

        split = layout.split(factor=0.6)
        b_split = split.row(align=True)
        row = b_split.row(align=True)
        row.operator(OctaneLoadPresetAll.bl_idname, text='Load All')
        row = b_split.row(align=True)
        row.operator(OctaneRenamePreset.bl_idname, text='Rename')
        row = b_split.row(align=True)
        row.operator(OctaneDeletePreset.bl_idname, text='Delete')

        col = layout.column()
        split = col.split(factor=0.75, align=True)
        split.label(text='Kernel')
        split.operator(OctaneLoadPresetKernel.bl_idname, text='Load')

        col = layout.column()
        split = col.split(factor=0.75, align=True)
        split.label(text='Environment')
        split.operator(OctaneLoadPresetEnvironment.bl_idname, text='Load')

        col = layout.column()
        split = col.split(factor=0.75, align=True)
        split.label(text='Imager')
        split.operator(OctaneLoadPresetImager.bl_idname, text='Load')
    
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        refresh_presets_list(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneAddPreset(Operator):
    bl_label = 'Add a preset'
    bl_idname = 'octane.add_preset'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        refresh_presets_list(context, True)
        return {'FINISHED'}

class OctaneLoadPresetKernel(Operator):
    bl_label = 'Load a preset kernel'
    bl_idname = 'octane.load_preset_kernel'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        preset = context.scene.oc_presets[context.scene.oc_presets_index]
        return preset.name != 'Default'

    def execute(self, context):
        preset = context.scene.oc_presets[context.scene.oc_presets_index].name
        load_preset_imager(context, preset)
        return {'FINISHED'}

class OctaneLoadPresetEnvironment(Operator):
    bl_label = 'Load a preset environment'
    bl_idname = 'octane.load_preset_environment'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        preset = context.scene.oc_presets[context.scene.oc_presets_index]
        return preset.name != 'Default'

    def execute(self, context):
        preset = context.scene.oc_presets[context.scene.oc_presets_index].name
        load_preset_environment(context, preset)
        return {'FINISHED'}

class OctaneLoadPresetImager(Operator):
    bl_label = 'Load a preset imager'
    bl_idname = 'octane.load_preset_imager'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        preset = context.scene.oc_presets[context.scene.oc_presets_index]
        return preset.name != 'Default'

    def execute(self, context):
        preset = context.scene.oc_presets[context.scene.oc_presets_index].name
        load_preset_imager(context, preset)
        return {'FINISHED'}

class OctaneLoadPresetAll(Operator):
    bl_label = 'Load a preset all'
    bl_idname = 'octane.load_preset_all'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        preset = context.scene.oc_presets[context.scene.oc_presets_index]
        return preset.name != 'Default'

    def execute(self, context):
        return {'FINISHED'}

class OctaneRenamePreset(Operator):
    bl_label = 'Rename a preset'
    bl_idname = 'octane.rename_preset'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.scene.oc_presets[context.scene.oc_presets_index].name != 'Default')

    def execute(self, context):
        refresh_presets_list(context)
        return {'FINISHED'}

class OctaneDeletePreset(Operator):
    bl_label = 'Delete a preset'
    bl_idname = 'octane.delete_preset'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.scene.oc_presets[context.scene.oc_presets_index].name != 'Default')
    
    def execute(self, context):
        refresh_presets_list(context, False, True)
        return {'FINISHED'}


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