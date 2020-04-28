import bpy
from bpy.types import Operator
from bl_operators.presets import AddPresetBase
from bpy.props import IntProperty, EnumProperty, BoolProperty, StringProperty, FloatVectorProperty
import os

def create_world_output(context, name):
    world = context.scene.world
    world.use_nodes = True
    outNode = world.node_tree.nodes.new('ShaderNodeOutputWorld')
    outNode.name = name
    ys = [node.location.y for node in world.node_tree.nodes if node.bl_idname == 'ShaderNodeOutputWorld']
    
    outNode.location = (300, min(ys)-800)
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

def update_backplate(self, context):
    world = context.scene.world
    ntree = world.node_tree
    outNode = ntree.get_output_node('octane')
    texenvNode = outNode.inputs['Octane VisibleEnvironment'].links[0].from_node
    texenvNode.inputs['Texture'].default_value = self.backplate_color

def get_enum_emissive_material(self, context):
    lights = context.scene.oc_lights
    index = context.scene.oc_lights_index
    # Return None if no object taged as light
    if(len(lights)==0): return [('None', 'None', '')]
    obj = lights[index].obj
    result = []

    if(obj.type == 'LIGHT'):
        # Return None if Light is not using nodes
        if(not obj.data.use_nodes): obj.data.use_nodes = True
        # Search node in the active light object for emissive node
        for node in obj.data.node_tree.nodes:
            if(node.bl_idname=='ShaderNodeOctBlackBodyEmission' or node.bl_idname=='ShaderNodeOctTextureEmission' or node.bl_idname=='ShaderNodeOctToonDirectionLight' or node.bl_idname=='ShaderNodeOctToonPointLight'):
                result.append(('Light', 'Light', ''))
    elif(obj.type == 'MESH'):
        # Return None if no material found in the active light object
        if(len(obj.material_slots)==0): return [('None', 'None', '')]
        # Search materials in the active light object for emissive material
        for slot in obj.material_slots:
            for node in slot.material.node_tree.nodes:
                if(node.bl_idname=='ShaderNodeOctBlackBodyEmission' or node.bl_idname=='ShaderNodeOctTextureEmission' or node.bl_idname=='ShaderNodeOctToonDirectionLight' or node.bl_idname=='ShaderNodeOctToonPointLight'):
                    result.append((slot.material.name, slot.material.name, ''))
    
    # Return result if the emissive material exists otherwise return None
    if(len(result)!=0): return result
    else: return [('None', 'None', '')]

def prop_node_attribute(node, layout, attribute, text):
    if(not node.inputs[attribute].is_linked):
        layout.prop(node.inputs[attribute], 'default_value', text=text)

def refresh_lights_list(context):
    context.scene.oc_lights.clear()
    context.scene.oc_lights_index = 0
    for obj in context.scene.objects:
        if 'oc_light' in obj:
            if(obj['oc_light']!='None' and obj['oc_light']!='' and obj['oc_light']!=None):
                light = context.scene.oc_lights.add()
                light.obj = obj
                light.tag = obj['oc_light']
                if(light.tag == 'Mesh'):
                    light.icon = 'LIGHTPROBE_CUBEMAP'
                elif(light.tag == 'Sphere'):
                    light.icon = 'LIGHT_POINT'
                elif(light.tag == 'Area'):
                    light.icon = 'LIGHT_AREA'
                elif(light.tag == 'Toon Point'):
                    light.icon = 'LIGHTPROBE_PLANAR'
                elif(light.tag == 'Toon Spot'):
                    light.icon = 'LIGHT_SPOT'
                else:
                    light.icon = 'QUESTION'

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
        scatteringFloatNode.inputs['Value'].default_value = 0.5
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

class OctaneOpenCompositor(Operator):
    bl_label = 'Open Compositor'
    bl_idname = 'octane.open_compositor'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.screen.userpref_show("INVOKE_DEFAULT")
        area = bpy.context.window_manager.windows[-1].screen.areas[0]
        area.ui_type = 'CompositorNodeTree'
        bpy.context.scene.use_nodes = True
        bpy.context.space_data.show_backdrop = True
        return {'FINISHED'}

class OctaneToggleClayMode(Operator):
    bl_label = 'Clay Mode'
    bl_idname = 'octane.toggle_claymode'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(context.scene.octane, 'clay_mode', text='')
        col.separator()
        col.operator('octane.add_backplate')
        col.operator('octane.remove_backplate')
        col.operator('octane.modify_backplate')

    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self) 

class OctaneAddBackplate(Operator):
    bl_label = 'Add Backplate'
    bl_idname = 'octane.add_backplate'
    bl_options = {'REGISTER', 'UNDO'}

    backplate_color: FloatVectorProperty(
        name="Color",
        size=4,
        default = (1, 1, 1, 1),
        min = 0,
        max = 1,
        subtype="COLOR")
    
    @classmethod
    def poll(cls, context):
        if(context.scene.world.use_nodes):
            world = context.scene.world
            ntree = world.node_tree
            outNode = ntree.get_output_node('octane')
            if(outNode):
                return (not outNode.inputs['Octane VisibleEnvironment'].is_linked)
            else:
                return False
        else:
            return False
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'backplate_color')
    
    def execute(self, context):
        world = context.scene.world
        ntree = world.node_tree
        outNode = ntree.get_output_node('octane')
        texenvNode = ntree.nodes.new('ShaderNodeOctTextureEnvironment')
        texenvNode.location = (outNode.location.x, outNode.location.y-200)
        texenvNode.inputs['Texture'].default_value = self.backplate_color
        texenvNode.inputs['Visable env Backplate'].default_value = True
        outNode = ntree.get_output_node('octane')
        ntree.links.new(texenvNode.outputs[0], outNode.inputs['Octane VisibleEnvironment'])
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneRemoveBackplate(Operator):
    bl_label = 'Remove Backplate'
    bl_idname = 'octane.remove_backplate'
    bl_options = {'REGISTER', 'UNDO'}
   
    @classmethod
    def poll(cls, context):
        if(context.scene.world.use_nodes):
            world = context.scene.world
            ntree = world.node_tree
            outNode = ntree.get_output_node('octane')
            if(outNode):
                return (outNode.inputs['Octane VisibleEnvironment'].is_linked)
            else:
                return False
        else:
            return False
    
    def execute(self, context):
        world = context.scene.world
        ntree = world.node_tree
        outNode = ntree.get_output_node('octane')
        link = outNode.inputs['Octane VisibleEnvironment'].links[0]
        ntree.nodes.remove(link.from_node)
        ntree.nodes.update()
        return {'FINISHED'}

class OctaneModifyBackplate(Operator):
    bl_label = 'Modify Backplate'
    bl_idname = 'octane.modify_backplate'
    bl_options = {'REGISTER', 'UNDO'}
   
    backplate_color: FloatVectorProperty(
        name="Color",
        size=4,
        default = (1, 1, 1, 1),
        min = 0,
        max = 1,
        subtype="COLOR",
        update=update_backplate)
    
    @classmethod
    def poll(cls, context):
        if(context.scene.world.use_nodes):
            world = context.scene.world
            ntree = world.node_tree
            outNode = ntree.get_output_node('octane')
            if(outNode):
                if (outNode.inputs['Octane VisibleEnvironment'].is_linked):
                    texenvNode = outNode.inputs['Octane VisibleEnvironment'].links[0].from_node
                    if (texenvNode.bl_idname == 'ShaderNodeOctTextureEnvironment'):
                        return not texenvNode.inputs['Texture'].is_linked
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'backplate_color')
    
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        world = context.scene.world
        ntree = world.node_tree
        outNode = ntree.get_output_node('octane')
        texenvNode = outNode.inputs['Octane VisibleEnvironment'].links[0].from_node
        self.backplate_color = texenvNode.inputs['Texture'].default_value
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneLightsManager(Operator):
    bl_label = 'Lights Manager'
    bl_idname = 'octane.lights_manager'
    bl_options = {'REGISTER', 'UNDO'}

    emissive_material: EnumProperty(
        name='Emissive Material',
        items=get_enum_emissive_material
    )

    def draw(self, context):
        lights = context.scene.oc_lights
        index = context.scene.oc_lights_index
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('octane.add_light_sphere', text='Sphere')
        row.operator('octane.add_light_area', text='Area')
        row = col.row(align=True)
        row.operator('octane.add_light_toon_point', text='Point (Toon)')
        row.operator('octane.add_light_toon_spot', text='Spot (Toon)')

        layout.template_list('OCTANE_UL_light_list', '', context.scene, 'oc_lights', context.scene, 'oc_lights_index')
        layout.prop(self, 'emissive_material', text='')
        if(self.emissive_material!='None' and self.emissive_material!='' and self.emissive_material!=None):
            obj = lights[index].obj
            if(obj.type=='LIGHT'):
                ntree = obj.data.node_tree
                if(obj.data.type == 'SPHERE'):
                    layout.prop(obj.data, 'sphere_radius', text='Radius')
                elif(obj.data.type == 'AREA'):
                    layout.prop(obj.data, 'shape', text='Shape')
                    if obj.data.shape in {'SQUARE', 'DISK'}:
                        layout.prop(obj.data, 'size', text='Size')
                    elif obj.data.shape in {'RECTANGLE', 'ELLIPSE'}:
                        layout.prop(obj.data, 'size', text='Size X')
                        layout.prop(obj.data, 'size_y', text='Size Y')
            else:
                ntree = bpy.data.materials[self.emissive_material].node_tree

            outNode = ntree.get_output_node('octane')
            if(outNode.inputs['Surface'].is_linked):
                if(outNode.inputs['Surface'].links[0].from_node.bl_idname=='ShaderNodeOctDiffuseMat'):
                    rootNode = outNode.inputs['Surface'].links[0].from_node
                    layout.template_node_view(ntree, rootNode, rootNode.inputs['Emission'])
                else:
                    rootNode = outNode
                    layout.template_node_view(ntree, rootNode, rootNode.inputs['Surface'])

    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        refresh_lights_list(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneSetLight(Operator):
    bl_label = 'Mark as a Light Source'
    bl_idname = 'octane.set_light'
    bl_options = {'REGISTER', 'UNDO'}

    light_type: EnumProperty(items=[
        ('None', 'None', ''),
        ('Mesh', 'Mesh', ''),
        ('Sphere', 'Sphere', ''),
        ('Area', 'Area', ''),
        ('Point Toon', 'Point(Toon)', ''),
        ('Spot Toon', 'Spot (Toon)', '')
    ], name='Type', default='None')

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'light_type', text='')
    
    def execute(self, context):
        for obj in context.selected_objects:
            if(self.light_type != 'None'):
                obj['oc_light'] = self.light_type
            else:
                if('oc_light' in obj):
                    del obj['oc_light']
        return {'FINISHED'}
    
    def invoke(self, context, event):
        if 'oc_light' in context.active_object:
            self.light_type = context.active_object['oc_light']

        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneAddLightSphere(Operator):
    bl_label = 'Add a sphere light'
    bl_idname = 'octane.add_light_sphere'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.light_add(type='SPHERE', location=(0, 0, 0))
        context.active_object['oc_light'] = 'Sphere'
        refresh_lights_list(context)
        return {'FINISHED'}

class OctaneAddLightArea(Operator):
    bl_label = 'Add a area light'
    bl_idname = 'octane.add_light_area'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.light_add(type='AREA', location=(0, 0, 0))
        context.active_object['oc_light'] = 'Area'
        refresh_lights_list(context)
        return {'FINISHED'}

class OctaneAddLightToonPoint(Operator):
    bl_label = 'Add a point toon light'
    bl_idname = 'octane.add_light_toon_point'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
        context.active_object['oc_light'] = 'Point Toon'
        refresh_lights_list(context)
        return {'FINISHED'}

class OctaneAddLightToonSpot(Operator):
    bl_label = 'Add a spot toon light'
    bl_idname = 'octane.add_light_toon_spot'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.light_add(type='SUN', location=(0, 0, 0))
        context.active_object['oc_light'] = 'Spot Toon'
        refresh_lights_list(context)
        return {'FINISHED'}

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

def remove_connected_nodes(ntree, node):
    for input in node.inputs:
        for link in input.links:
            remove_connected_nodes(ntree, link.from_node)
            ntree.nodes.remove(link.from_node)

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

class OctaneEnvironmentsManager(Operator):
    bl_label = 'Environments manager'
    bl_idname = 'octane.environments_manager'
    bl_options = {'REGISTER', 'UNDO'}

    #preset: EnumProperty(name='Presets', items=get_enum_env_presets, update=update_enum_env_presets)

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

        #if(self.preset != context.scene.selected_env_preset):
        #    if(self.preset==''):
        #        self.preset = 'None'
        #    self.preset = context.scene.selected_env_preset

        # Draw Presets
        #row = layout.row(align=True)
        #row.prop(self, 'preset', text='Presets')
        #row.operator(OctaneAddEnvironmentPreset.bl_idname, text='', icon='ADD')
        #row.operator(OctaneRemoveEnvironmentPreset.bl_idname, text='', icon='REMOVE').preset_name = self.preset
        
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
        #self.preset = context.scene.selected_env_preset
        refresh_worlds_list(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self)