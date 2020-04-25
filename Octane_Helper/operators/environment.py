import bpy
from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty, BoolProperty, StringProperty, FloatVectorProperty

def create_world(name):
    world = bpy.data.worlds.new(name)
    world.use_nodes = True
    return world

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
    nodes = world.node_tree.nodes
    outNode = [node for node in nodes if node.type=='OUTPUT_WORLD'][0]
    texenvNode = outNode.inputs['Octane VisibleEnvironment'].links[0].from_node
    texenvNode.inputs['Texture'].default_value = self.backplate_color

def get_enum_emissive_materials(self, context):
    lights = context.scene.oc_lights
    index = context.scene.oc_lights_index
    # Return None if no object taged as light
    if(len(lights)==0): return [('None', 'None', '')]
    obj = context.scene.objects[lights[index].name]
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
    for obj in context.scene.objects:
        if 'oc_light' in obj:
            if(obj['oc_light']!='None' and obj['oc_light']!='' and obj['oc_light']!=None):
                light = context.scene.oc_lights.add()
                light.name = obj.name
                light.tag = obj['oc_light']
                if(light.tag == 'Mesh'):
                    light.icon = 'LIGHTPROBE_CUBEMAP'
                elif(light.tag == 'Sphere'):
                    light.icon = 'LIGHT_POINT'
                elif(light.tag == 'Area'):
                    light.icon = 'LIGHT_AREA'
                elif(light.tag == 'Toon'):
                    light.icon = 'LIGHTPROBE_PLANAR'
                else:
                    light.icon = 'QUESTION'

# Classes
class OctaneSetupHDRIEnv(Operator):
    bl_label = 'Setup'
    bl_idname = 'octane.setup_hdri'
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.hdr;*.png;*.jpeg;*.jpg;*.exr", options={"HIDDEN"})
    enable_overwrite: BoolProperty(
        name="Overwrite",
        default=True)
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
            world = create_world('OC_Environment')
            nodes = world.node_tree.nodes
            imgNode = nodes.new('ShaderNodeOctImageTex')
            imgNode.location = (-210, 300)
            imgNode.inputs['Gamma'].default_value = 1
            imgNode.image = bpy.data.images.load(self.filepath)
            sphereNode = nodes.new('ShaderNodeOctSphericalProjection')
            sphereNode.location = (-410, 100)
            transNode = nodes.new('ShaderNodeOct3DTransform')
            transNode.location = (-610, 100)
            transNode.name = 'Texture_3D_Transform'
            if(self.enable_backplate):
                texenvNode = nodes.new('ShaderNodeOctTextureEnvironment')
                texenvNode.location = (10, 0)
                texenvNode.inputs['Texture'].default_value = self.backplate_color
                texenvNode.inputs['Visable env Backplate'].default_value = True
                world.node_tree.links.new(texenvNode.outputs[0], nodes[0].inputs['Octane VisibleEnvironment'])
            world.node_tree.links.new(transNode.outputs[0], sphereNode.inputs['Sphere Transformation'])
            world.node_tree.links.new(sphereNode.outputs[0], imgNode.inputs['Projection'])
            world.node_tree.links.new(imgNode.outputs[0], nodes[1].inputs['Texture'])
            context.scene.world = world
            # Setting up the octane
            if self.enable_overwrite:
                context.scene.display_settings.display_device = 'None'
                context.scene.view_settings.exposure = 0
                context.scene.view_settings.gamma = 1
                context.scene.octane.hdr_tonemap_preview_enable = True
                context.scene.octane.use_preview_setting_for_camera_imager = True
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

class OctaneSetRenderID(Operator):
    bl_label = 'Set Render Layer ID'
    bl_idname = 'octane.set_renderid'
    bl_options = {'REGISTER', 'UNDO'}

    rid: IntProperty(
        name = 'Render Layer ID',
        min = 1,
        max = 255,
        step = 1,
        default = 1
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None)

    def execute(self, context):
        for obj in context.selected_objects:
            obj.octane.render_layer_id = self.rid
            obj.data.update()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

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
            nodes = context.scene.world.node_tree.nodes
            outNode = [node for node in nodes if node.type=='OUTPUT_WORLD'][0]
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
        nodes = world.node_tree.nodes
        texenvNode = nodes.new('ShaderNodeOctTextureEnvironment')
        texenvNode.location = (10, 0)
        texenvNode.inputs['Texture'].default_value = self.backplate_color
        texenvNode.inputs['Visable env Backplate'].default_value = True
        outNode = [node for node in nodes if node.type=='OUTPUT_WORLD'][0]
        world.node_tree.links.new(texenvNode.outputs[0], outNode.inputs['Octane VisibleEnvironment'])
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
            nodes = context.scene.world.node_tree.nodes
            outNode = [node for node in nodes if node.type=='OUTPUT_WORLD'][0]
            if(outNode):
                return (outNode.inputs['Octane VisibleEnvironment'].is_linked)
            else:
                return False
        else:
            return False
    
    def execute(self, context):
        world = context.scene.world
        nodes = world.node_tree.nodes
        outNode = [node for node in nodes if node.type=='OUTPUT_WORLD'][0]
        link = outNode.inputs['Octane VisibleEnvironment'].links[0]
        nodes.remove(link.from_node)
        nodes.update()
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
            nodes = context.scene.world.node_tree.nodes
            outNode = [node for node in nodes if node.type=='OUTPUT_WORLD'][0]
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
        nodes = world.node_tree.nodes
        outNode = [node for node in nodes if node.type=='OUTPUT_WORLD'][0]
        texenvNode = outNode.inputs['Octane VisibleEnvironment'].links[0].from_node
        self.backplate_color = texenvNode.inputs['Texture'].default_value
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneLightsManager(Operator):
    bl_label = 'Lights Manager'
    bl_idname = 'octane.lights_manager'
    bl_options = {'REGISTER', 'UNDO'}

    emissive_materials: EnumProperty(
        name='Emissive Materials',
        items=get_enum_emissive_materials
    )

    def draw(self, context):
        lights = context.scene.oc_lights
        index = context.scene.oc_lights_index
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('octane.add_light_sphere', text='Sphere')
        row.operator('octane.add_light_area', text='Area')
        row.operator('octane.add_light_toon', text='Toon')

        layout.template_list('OCTANE_UL_light_list', '', context.scene, 'oc_lights', context.scene, 'oc_lights_index')
        layout.prop(self, 'emissive_materials', text='')
        if(self.emissive_materials!='None' and self.emissive_materials!='' and self.emissive_materials!=None):
            obj = context.scene.objects[lights[index].name]
            if(obj.type=='LIGHT'):
                nodes = obj.data.node_tree.nodes
            else:
                nodes = bpy.data.materials[self.emissive_materials].node_tree.nodes
            for node in nodes:
                if(node.bl_idname=='ShaderNodeOctBlackBodyEmission' or node.bl_idname=='ShaderNodeOctTextureEmission' or node.bl_idname=='ShaderNodeOctToonDirectionLight' or node.bl_idname=='ShaderNodeOctToonPointLight'):
                    if(node.inputs['Texture'].is_linked):
                        if(node.inputs['Texture'].links[0].from_node.bl_idname=='ShaderNodeOctRGBSpectrumTex'):
                            layout.prop(node.inputs['Texture'].links[0].from_node.inputs['Color'], 'default_value', text='Color')
                    else:
                        layout.prop(node.inputs['Texture'], 'default_value', text='Texture')
                    prop_node_attribute(node, layout, 'Power', 'Power')
                    #prop_node_attribute(node, layout, 'Light pass ID', 'Light pass ID')
                    prop_node_attribute(node, layout, 'Cast shadows', 'Cast shadows')
                if(node.bl_idname=='ShaderNodeOctBlackBodyEmission'):
                    prop_node_attribute(node, layout, 'Surface brightness', 'Surface brightness')
                    prop_node_attribute(node, layout, 'Keep instance power', 'Keep instance power')
                    prop_node_attribute(node, layout, 'Double-sided', 'Double-sided')
                    prop_node_attribute(node, layout, 'Temperature', 'Temperature')
                    prop_node_attribute(node, layout, 'Normalize', 'Normalize')
                    prop_node_attribute(node, layout, 'Distribution', 'Distribution')
                    prop_node_attribute(node, layout, 'Sampling Rate', 'Sampling Rate')
                    prop_node_attribute(node, layout, 'Visible on diffuse', 'Visible on diffuse')
                    prop_node_attribute(node, layout, 'Visible on specular', 'Visible on specular')
                    prop_node_attribute(node, layout, 'Transparent emission', 'Transparent emission')
                if(node.bl_idname=='ShaderNodeOctTextureEmission'):
                    prop_node_attribute(node, layout, 'Surface brightness', 'Surface brightness')
                    prop_node_attribute(node, layout, 'Keep instance power', 'Keep instance power')
                    prop_node_attribute(node, layout, 'Double-sided', 'Double-sided')
                    prop_node_attribute(node, layout, 'Distribution', 'Distribution')
                    prop_node_attribute(node, layout, 'Sampling Rate', 'Sampling Rate')
                    prop_node_attribute(node, layout, 'Visible on diffuse', 'Visible on diffuse')
                    prop_node_attribute(node, layout, 'Visible on specular', 'Visible on specular')
                    prop_node_attribute(node, layout, 'Transparent emission', 'Transparent emission')

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
        ('Toon', 'Toon', ''),
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

class OctaneAddLightToon(Operator):
    bl_label = 'Add a toon light'
    bl_idname = 'octane.add_light_toon'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
        context.active_object['oc_light'] = 'Point'
        refresh_lights_list(context)
        return {'FINISHED'}