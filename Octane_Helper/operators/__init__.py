import bpy
from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty, BoolProperty, StringProperty, FloatVectorProperty, FloatProperty
import bmesh

def get_enum_trs(self, context):
    world = context.scene.world
    items = [(node.name, node.name, '') for node in world.node_tree.nodes if node.type=='OCT_3D_TRN']
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

def create_material(context, name, root):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    outNode = nodes[0]
    oldMainMat = nodes[1]
    mainMat = nodes.new(root)
    mainMat.location = oldMainMat.location
    if('Smooth' in mainMat.inputs):
        mainMat.inputs['Smooth'].default_value = context.scene.is_smooth
    nodes.remove(oldMainMat)
    mat.node_tree.links.new(outNode.inputs['Surface'], mainMat.outputs[0])
    return mat

def assign_material(context, mat):
    # Object mode
    if(context.mode == 'OBJECT'):
        for obj in context.selected_objects:
            if(obj.type == 'MESH'):
                obj.active_material = mat
    # Edit mode
    elif(context.mode == 'EDIT_MESH'):
        for obj in context.selected_objects:
            if(obj.type == 'MESH'):
                bm = bmesh.from_edit_mesh(obj.data)
                for face in bm.faces:
                    if face.select:
                        # If no base material found, create one
                        if (len(obj.material_slots)==0):
                            obj.active_material = create_material(mat.name + '_Base', type)
                        obj.data.materials.append(mat)
                        obj.active_material_index = len(obj.material_slots) - 1
                        face.material_index = len(obj.material_slots) - 1
                obj.data.update()

def create_world(name):
    world = bpy.data.worlds.new(name)
    world.use_nodes = True
    return world

# Operators
class OctaneAssignUniversal(Operator):
    bl_label = 'Universal Material'
    bl_idname = 'octane.assign_universal'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Universal', 'ShaderNodeOctUniversalMat')
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignDiffuse(Operator):
    bl_label = 'Diffuse Material'
    bl_idname = 'octane.assign_diffuse'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Diffuse', 'ShaderNodeOctDiffuseMat')
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignEmissive(Operator):
    bl_label = 'Emissive Material'
    bl_idname = 'octane.assign_emissive'
    bl_options = {'REGISTER', 'UNDO'}

    rgb_emission_color: FloatVectorProperty(
        name="Color",
        size=4,
        default = (1, 1, 1, 1),
        min = 0,
        max = 1,
        subtype="COLOR")
    
    emission_power: FloatProperty(
        name="Power", 
        default=10, 
        min=0.0001,
        step=10, 
        precision=4)
    
    emission_surface_brightness: BoolProperty(
        name="Surface Brightness",
        default=True)

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Emissive', 'ShaderNodeOctDiffuseMat')
        nodes = mat.node_tree.nodes
        emissionNode = nodes.new('ShaderNodeOctBlackBodyEmission')
        emissionNode.location = (-210, 300)
        emissionNode.inputs['Power'].default_value = self.emission_power
        emissionNode.inputs['Surface brightness'].default_value = self.emission_surface_brightness
        rgbNode = nodes.new('ShaderNodeOctRGBSpectrumTex')
        rgbNode.location = (-410, 300)
        rgbNode.inputs['Color'].default_value = self.rgb_emission_color
        mat.node_tree.links.new(rgbNode.outputs[0], emissionNode.inputs['Texture'])
        mat.node_tree.links.new(emissionNode.outputs[0], nodes[1].inputs['Emission'])
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneAssignGlossy(Operator):
    bl_label = 'Glossy Material'
    bl_idname = 'octane.assign_glossy'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Glossy', 'ShaderNodeOctGlossyMat')
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignSpecular(Operator):
    bl_label = 'Specular Material'
    bl_idname = 'octane.assign_specular'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Specular', 'ShaderNodeOctSpecularMat')
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignMix(Operator):
    bl_label = 'Mix Material'
    bl_idname = 'octane.assign_mix'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Mix', 'ShaderNodeOctMixMat')
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignPortal(Operator):
    bl_label = 'Portal Material'
    bl_idname = 'octane.assign_portal'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Portal', 'ShaderNodeOctPortalMat')
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignShadowCatcher(Operator):
    bl_label = 'ShadowCatcher Material'
    bl_idname = 'octane.assign_shadowcatcher'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_ShadowCatcher', 'ShaderNodeOctShadowCatcherMat')
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignToon(Operator):
    bl_label = 'Toon Material'
    bl_idname = 'octane.assign_toon'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Toon', 'ShaderNodeOctToonMat')
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignMetal(Operator):
    bl_label = 'Metal Material'
    bl_idname = 'octane.assign_metal'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Metal', 'ShaderNodeOctMetalMat')
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignLayered(Operator):
    bl_label = 'Layered Material'
    bl_idname = 'octane.assign_layered'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Layered', 'ShaderNodeOctLayeredMat')
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignComposite(Operator):
    bl_label = 'Composite Material'
    bl_idname = 'octane.assign_composite'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Composite', 'ShaderNodeOctCompositeMat')
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignHair(Operator):
    bl_label = 'Hair Material'
    bl_idname = 'octane.assign_hair'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Hair', 'ShaderNodeOctHairMat')
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneCopyMat(Operator):
    bl_label = 'Copy'
    bl_idname = 'octane.copy_mat'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if(obj.type == 'MESH'):
            if(len(obj.material_slots)>=1):
                bpy.types.Material.copied_mat = obj.active_material
        return {'FINISHED'}

class OctanePasteMat(Operator):
    bl_label = 'Paste'
    bl_idname = 'octane.paste_mat'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (bpy.types.Material.copied_mat is not None)
    def execute(self, context):
        if(bpy.types.Material.copied_mat):
            assign_material(context, bpy.types.Material.copied_mat)
        return {'FINISHED'}

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
        if(len([node for node in world.node_tree.nodes if node.type=='OCT_3D_TRN'])):
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

    def execute(self, context):
        for obj in context.selected_objects:
            obj.octane.render_layer_id = self.rid
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
    bl_label = 'Claymode'
    bl_idname = 'octane.toggle_claymode'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(context.scene.octane, 'clay_mode', text='')
        col.operator('octane.add_backplate')
        col.operator('octane.remove_backplate')

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
                    if (texenvNode.type == 'OCT_TEXTURE_ENVIRONMENT'):
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

class OctaneManagePostprocess(Operator):
    bl_label = 'Postprocess'
    bl_idname = 'octane.manage_postprocess'
    bl_options = {'REGISTER', 'UNDO'}
    
    def draw(self, context):
        oct_cam = context.scene.oct_view_cam
        layout = self.layout
        col = layout.column(align=True)
        col.prop(context.scene.oct_view_cam, "postprocess", text="Enable Postprocess")
        col.prop(context.scene.octane, "use_preview_post_process_setting")
        col = layout.column(align=True)
        col.enabled = context.scene.oct_view_cam.postprocess
        col.prop(oct_cam, "cut_off")
        col.prop(oct_cam, "bloom_power")
        col.prop(oct_cam, "glare_power")
        col = layout.column(align=True)
        col.enabled = context.scene.oct_view_cam.postprocess
        col.prop(oct_cam, "glare_ray_count")
        col.prop(oct_cam, "glare_angle")
        col.prop(oct_cam, "glare_blur")
        col.prop(oct_cam, "spectral_intencity")
        col.prop(oct_cam, "spectral_shift")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

classes = (
    OctaneAssignUniversal,
    OctaneAssignDiffuse,
    OctaneAssignEmissive,
    OctaneAssignGlossy,
    OctaneAssignSpecular,
    OctaneAssignMix,
    OctaneAssignPortal,
    OctaneAssignShadowCatcher,
    OctaneAssignToon,
    OctaneAssignMetal,
    OctaneAssignLayered,
    OctaneAssignComposite,
    OctaneAssignHair,
    OctaneCopyMat,
    OctanePasteMat,
    OctaneSetupHDRIEnv,
    OctaneSetRenderID,
    OctaneTransformHDRIEnv,
    OctaneOpenCompositor,
    OctaneToggleClayMode,
    OctaneAddBackplate,
    OctaneRemoveBackplate,
    OctaneModifyBackplate,
    OctaneManagePostprocess
)

def register_operators():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister_operators():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)