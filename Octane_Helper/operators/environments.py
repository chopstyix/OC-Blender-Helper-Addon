import bpy 
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty, StringProperty, FloatVectorProperty
import os

env_path = os.path.join(bpy.utils.preset_paths('octane')[0], 'environments')

def get_y(world, type):
    if(not world.node_tree.get_output_node('octane')):
        return 0
    ys = [node.location.y for node in world.node_tree.nodes if node.bl_idname == 'ShaderNodeOutputWorld']
    if(type == 'Min'):
        return min(ys)
    elif(type == 'Max'):
        return max(ys)

def create_world_output(context, name):
    world = context.scene.world
    world.use_nodes = True
    outNode = world.node_tree.nodes.new('ShaderNodeOutputWorld')
    outNode.name = name
    
    outNode.location = (300, get_y(world, 'Min')-800)
    return outNode

def get_enum_trs(self, context):
    world = context.scene.world
    items = [(node.name, node.name, '') for node in world.node_tree.nodes if node.bl_idname=='ShaderNodeOct3DTransform']
    return items

def update_enum_trs(self, context):
    world = context.scene.world
    self.rotation = world.node_tree.nodes[self.transNodes].inputs['Rotation'].default_value
    self.scale = world.node_tree.nodes[self.transNodes].inputs['Scale'].default_value
    self.translation = world.node_tree.nodes[self.transNodes].inputs['Translation'].default_value

def update_hdri_rotation(self, context):
    world = context.scene.world
    world.node_tree.nodes[self.transNodes].inputs['Rotation'].default_value = self.rotation

def update_hdri_scale(self, context):
    world = context.scene.world
    world.node_tree.nodes[self.transNodes].inputs['Scale'].default_value = self.scale

def update_hdri_translation(self, context):
    world = context.scene.world
    world.node_tree.nodes[self.transNodes].inputs['Translation'].default_value = self.translation

def refresh_worlds_list(context, active_last=False):
    context.scene.oc_worlds.clear()
    
    ntree = context.scene.world.node_tree
    count = 0
    active = 0
    for node in ntree.nodes:
        if(node.bl_idname=='ShaderNodeOutputWorld'):
            world = context.scene.oc_worlds.add()
            world.node = node.name
            if(node.is_active_output):
                active = count
            count += 1
    
    if(active_last):
        context.scene.oc_worlds_index = len(context.scene.oc_worlds) - 1
        bpy.ops.octane.activate_env()
    else:
        context.scene.oc_worlds_index = active

def remove_connected_nodes(ntree, node):
    for input in node.inputs:
        for link in input.links:
            remove_connected_nodes(ntree, link.from_node)
            ntree.nodes.remove(link.from_node)

def get_enum_env_presets(self, context):
    if not os.path.isdir(env_path):
        os.makedirs(env_path)
    presets = ['Default'] + [path[:-6] for path in os.listdir(env_path)]
    return [(preset, preset, '') for preset in presets]

def append_env_nodes(ntree_to, rootNodes, offset_y):
    for rootNode in rootNodes:
        root_new = ntree_to.nodes.new(rootNode.bl_idname)
        root_new.name = rootNode.name
        root_new.location.x = rootNode.location.x
        root_new.location.y = rootNode.location.y + offset_y - 800
        for input in rootNode.inputs:
            if(not input.is_linked):
                if('default_value' in dir(input)):
                    root_new.inputs[input.identifier].default_value = input.default_value
            else:
                linked_nodes = [link.from_node for link in input.links]
                for linked_node in linked_nodes:
                    sub = append_env_nodes(ntree_to, [linked_node], offset_y)
                    ntree_to.links.new(sub.outputs[0], root_new.inputs[input.identifier])
        if(len(rootNodes) == 0 or len(rootNodes) == 1):
            return root_new

# Classes
class OctaneEnvironmentsManager(Operator):
    bl_label = 'Environments manager'
    bl_idname = 'octane.environments_manager'
    bl_options = {'REGISTER'}

    category: EnumProperty(
        name='Category', 
        items=[
            ('Environment', 'Environment', ''),
            ('Visible Environment', 'Visible Environment', ''),
        ])

    def draw(self, context):
        ntree = context.scene.world.node_tree
        index = context.scene.oc_worlds_index
        layout = self.layout

        # Draw presets
        row = layout.row(align=True)
        row.prop(context.scene, 'oc_env_preset', text='Preset')
        row.operator(OctaneAppendEnvironmentPreset.bl_idname, text='', icon='DOWNARROW_HLT')
        row.operator(OctaneAddEnvironmentPreset.bl_idname, text='', icon='ADD')
        row.operator(OctaneRemoveEnvironmentPreset.bl_idname, text='', icon='REMOVE')

        # Draw Worlds
        row = layout.row(align=True)
        row.template_list('OCTANE_UL_world_list', '', context.scene, 'oc_worlds', context.scene, 'oc_worlds_index')
        sub = row.column(align=True)
        sub.operator(OctaneAddTexEnv.bl_idname, text='', icon='IMAGE_PLANE')
        sub.operator(OctaneAddSkyEnv.bl_idname, text='', icon='LIGHT_SUN')
        sub.operator(OctaneAddMedEnv.bl_idname, text='', icon='GHOST_ENABLED')
        
        # Draw nodes view
        if(len(context.scene.oc_worlds)!=0):
            rootNode = ntree.nodes[context.scene.oc_worlds[index].node]
            split = layout.split(factor=0.6)
            b_split = split.row(align=True)
            row = b_split.row(align=True)
            row.enabled = (not ntree.nodes[context.scene.oc_worlds[index].node].is_active_output)
            row.operator(OctaneActivateEnvironment.bl_idname, text='Activate')
            row = b_split.row(align=True)
            row.operator(OctaneRenameEnvironment.bl_idname, text='Rename')
            row = b_split.row(align=True)
            row.operator(OctaneDeleteEnvironment.bl_idname, text='Delete')
            
            split.prop(self, 'category', text='')
            if(self.category == 'Environment'):
                layout.template_node_view(ntree, rootNode, rootNode.inputs['Octane Environment'])
            elif(self.category == 'Visible Environment'):
                layout.template_node_view(ntree, rootNode, rootNode.inputs['Octane VisibleEnvironment'])
        else:
            layout.label(text='No World Output found')
    
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        if(not context.scene.world):
            world = bpy.data.worlds.new('World')
            world.use_nodes = True
        if(context.scene.oc_env_preset == ''):
            context.scene.oc_env_preset = 'Default'
        refresh_worlds_list(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneAppendEnvironmentPreset(Operator):
    bl_label = 'Append env preset'
    bl_idname = 'octane.append_env_preset'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if(context.scene.oc_env_preset !='Default'):
            prev_worlds = [world.name for world in bpy.data.worlds]
            path = os.path.join(env_path, context.scene.oc_env_preset + '.blend')
            with bpy.data.libraries.load(path) as (data_from, data_to):
                data_to.worlds = data_from.worlds
            curr_worlds = [world.name for world in bpy.data.worlds]
            added_world = bpy.data.worlds[list(set(curr_worlds)-set(prev_worlds))[0]]
            
            # Append nodes to the current world
            ntree_from = added_world.node_tree
            ntree_to = context.scene.world.node_tree
            outNodes = [node for node in ntree_from.nodes if node.bl_idname == 'ShaderNodeOutputWorld']
            offset_y = get_y(context.scene.world, 'Min') - get_y(added_world, 'Max')
            append_env_nodes(ntree_to, outNodes, offset_y)
            
            bpy.data.worlds.remove(added_world)
            refresh_worlds_list(context)
        return {'FINISHED'}

class OctaneAddEnvironmentPreset(Operator):
    bl_label = 'Add env preset'
    bl_idname = 'octane.add_env_preset'
    bl_options = {'REGISTER', 'UNDO'}
    
    save_name: StringProperty(name='Name', default='')
    pack_images: BoolProperty(name='Pack images', default=False, description='This option may take long time to process. Turn on only when you need to share presets across computers')

    def draw(self, context):
        layout = self.layout
        layout.label(text='This will save your world nodes to a file')
        col = layout.column(align=True)
        col.prop(self, 'save_name')
        col.prop(self, 'pack_images')
    
    def execute(self, context):
        # Create a Blend file
        if(self.save_name==''): 
            self.report({'WARNING'}, 'The name should not be empty')
            return {'CANCELLED'}
        if(self.save_name=='Default'): 
            self.report({'WARNING'}, 'The name is invalid')
            return {'CANCELLED'}

        files = os.listdir(env_path)
        if(len([file for file in files if (file[:-6]==self.save_name)])):
            self.report({'WARNING'}, 'The name has beed used, try another one')
            return {'CANCELLED'}
        
        save_file = os.path.join(env_path, self.save_name + '.blend')

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

        context.scene.oc_env_preset = self.save_name
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneRemoveEnvironmentPreset(Operator):
    bl_label = 'Remove env preset'
    bl_idname = 'octane.remove_env_preset'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if(context.scene.oc_env_preset == '' or context.scene.oc_env_preset == 'Default'):
            self.report({'WARNING'}, 'Nothing is removed')
            return {'CANCELLED'}
        
        os.remove(os.path.join(env_path, context.scene.oc_env_preset + '.blend'))

        context.scene.oc_env_preset = 'Default'

        return {'FINISHED'}

class OctaneActivateEnvironment(Operator):
    bl_label = 'Activate an environment'
    bl_idname = 'octane.activate_env'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ntree = context.scene.world.node_tree
        index = context.scene.oc_worlds_index
        
        outNodes = [node for node in ntree.nodes if node.bl_idname == 'ShaderNodeOutputWorld']

        if(len(outNodes)):
            for outNode in outNodes:
                outNode.is_active_output = False

        ntree.nodes[context.scene.oc_worlds[index].node].is_active_output = True

        refresh_worlds_list(context)

        return {'FINISHED'}

class OctaneRenameEnvironment(Operator):
    bl_label = 'Rename an environment'
    bl_idname = 'octane.rename_env'
    bl_options = {'REGISTER', 'UNDO'}

    name: StringProperty(name='Name', default='')

    def execute(self, context):
        ntree = context.scene.world.node_tree
        index = context.scene.oc_worlds_index
        ntree.nodes[context.scene.oc_worlds[index].node].name = self.name
        refresh_worlds_list(context)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        ntree = context.scene.world.node_tree
        index = context.scene.oc_worlds_index
        self.name = context.scene.oc_worlds[index].node
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneDeleteEnvironment(Operator):
    bl_label = 'Delete an environment'
    bl_idname = 'octane.delete_env'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ntree = context.scene.world.node_tree
        index = context.scene.oc_worlds_index
        outNode = ntree.nodes[context.scene.oc_worlds[index].node]

        remove_connected_nodes(ntree, outNode)
        ntree.nodes.remove(outNode)
        
        ntree.nodes.update()

        refresh_worlds_list(context)
        return {'FINISHED'}

class OctaneAddSkyEnv(Operator):
    bl_label = 'Setup Sky'
    bl_idname = 'octane.add_tex_sky'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ntree = context.scene.world.node_tree
        outNode = create_world_output(context, 'OC_Sky_Env')
        skyenvNode = ntree.nodes.new('ShaderNodeOctDaylightEnvironment')
        skyenvNode.location = (outNode.location.x - 200, outNode.location.y)
        ntree.links.new(skyenvNode.outputs[0], outNode.inputs['Octane Environment'])
        # Setting up the octane
        context.scene.display_settings.display_device = 'None'
        context.scene.view_settings.exposure = 0
        context.scene.view_settings.gamma = 1
        context.scene.octane.hdr_tonemap_preview_enable = True

        refresh_worlds_list(context, True)
        
        return {'FINISHED'}

class OctaneAddMedEnv(Operator):
    bl_label = 'Setup Medium'
    bl_idname = 'octane.add_med_env'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ntree = context.scene.world.node_tree
        outNode = create_world_output(context, 'OC_Med_Env')
        skyenvNode = ntree.nodes.new('ShaderNodeOctDaylightEnvironment')
        skyenvNode.location = (outNode.location.x - 200, outNode.location.y)
        skyenvNode.inputs['Medium radius'].default_value = 100
        mediumNode = ntree.nodes.new('ShaderNodeOctVolumeMedium')
        mediumNode.location = (skyenvNode.location.x - 200, skyenvNode.location.y - 200)
        mediumNode.inputs['Density'].default_value = 1.0
        mediumNode.inputs['Invert abs.'].default_value = False
        absFloatNode = ntree.nodes.new('ShaderNodeOctFloatTex')
        absFloatNode.inputs['Value'].default_value = 0.0
        absFloatNode.location = (mediumNode.location.x - 200, mediumNode.location.y - 100)
        scatteringFloatNode = ntree.nodes.new('ShaderNodeOctFloatTex')
        scatteringFloatNode.inputs['Value'].default_value = 0.1
        scatteringFloatNode.location = (absFloatNode.location.x, absFloatNode.location.y - 100)
        ntree.links.new(scatteringFloatNode.outputs[0], mediumNode.inputs['Scattering Tex'])
        ntree.links.new(absFloatNode.outputs[0], mediumNode.inputs['Absorption Tex'])
        ntree.links.new(mediumNode.outputs[0], skyenvNode.inputs['Medium'])
        ntree.links.new(skyenvNode.outputs[0], outNode.inputs['Octane Environment'])
        # Setting up the octane
        context.scene.display_settings.display_device = 'None'
        context.scene.view_settings.exposure = 0
        context.scene.view_settings.gamma = 1
        context.scene.octane.hdr_tonemap_preview_enable = True

        refresh_worlds_list(context, True)
        
        return {'FINISHED'}

class OctaneAddTexEnv(Operator):
    bl_label = 'Setup Texture'
    bl_idname = 'octane.add_tex_env'
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.hdr;*.png;*.jpeg;*.jpg;*.exr", options={"HIDDEN"})
    name: StringProperty(
        name='Name',
        default='OC_Tex_Env'
    )
    enable_override: BoolProperty(
        name="Override Camera Settings",
        default=False)
    enable_backplate: BoolProperty(
        name="Backplate",
        default=False)
    backplate_color: FloatVectorProperty(
        name="",
        size=4,
        default = (1, 1, 1, 1),
        min = 0,
        max = 1,
        subtype="COLOR")

    def execute(self, context):
        if self.filepath != '':
            ntree = context.scene.world.node_tree
            outNode = create_world_output(context, self.name)
            texenvNode = ntree.nodes.new('ShaderNodeOctTextureEnvironment')
            texenvNode.location = (outNode.location.x - 200, outNode.location.y)
            imgNode = ntree.nodes.new('ShaderNodeOctImageTex')
            imgNode.location = (texenvNode.location.x - 250, outNode.location.y)
            imgNode.inputs['Gamma'].default_value = 1
            imgNode.image = bpy.data.images.load(self.filepath)
            sphereNode = ntree.nodes.new('ShaderNodeOctSphericalProjection')
            sphereNode.location = (imgNode.location.x - 200, outNode.location.y)
            transNode = ntree.nodes.new('ShaderNodeOct3DTransform')
            transNode.location = (sphereNode.location.x-200, outNode.location.y)
            transNode.name = '3D_Transform'
            if(self.enable_backplate):
                texvisNode = ntree.nodes.new('ShaderNodeOctTextureEnvironment')
                texvisNode.location = (texenvNode.location.x, texenvNode.location.y-300)
                texvisNode.inputs['Texture'].default_value = self.backplate_color
                texvisNode.inputs['Visable env Backplate'].default_value = True
                ntree.links.new(texvisNode.outputs[0], outNode.inputs['Octane VisibleEnvironment'])
            ntree.links.new(transNode.outputs[0], sphereNode.inputs['Sphere Transformation'])
            ntree.links.new(sphereNode.outputs[0], imgNode.inputs['Projection'])
            ntree.links.new(imgNode.outputs[0], texenvNode.inputs['Texture'])
            ntree.links.new(texenvNode.outputs[0], outNode.inputs['Octane Environment'])
            # Setting up the octane
            context.scene.display_settings.display_device = 'None'
            context.scene.view_settings.exposure = 0
            context.scene.view_settings.gamma = 1
            context.scene.octane.hdr_tonemap_preview_enable = True
            if self.enable_override:
                context.scene.octane.use_preview_setting_for_camera_imager = True
            refresh_worlds_list(context, True)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

class OctaneTransformHDRIEnv(Operator):
    bl_label = 'Transform Texture Environment'
    bl_idname = 'octane.transform_hdri'
    bl_options = {'REGISTER', 'UNDO'}

    transNodes: EnumProperty(items=get_enum_trs, name='Nodes', update=update_enum_trs)

    rotation: FloatVectorProperty(name='Rotation', precision=3, step=10, min=-360, max=360, update=update_hdri_rotation)
    scale: FloatVectorProperty(name='Scale', precision=3, step=10, update=update_hdri_scale)
    translation: FloatVectorProperty(name='Translation', subtype='TRANSLATION', step=10, precision=3, update=update_hdri_translation)

    @classmethod
    def poll(cls, context):
        world = context.scene.world
        if(len([node for node in world.node_tree.nodes if node.bl_idname=='ShaderNodeOct3DTransform'])):
            return True
        else:
            return False
    def execute(self, context):
        return {'FINISHED'}
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'transNodes', text='')
        col.prop(self, 'rotation')
        col.prop(self, 'scale')
        col.prop(self, 'translation')
    def invoke(self, context, event):
        update_enum_trs(self, context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self)