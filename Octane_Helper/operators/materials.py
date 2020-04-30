import bpy, bmesh
from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty, BoolProperty, StringProperty, FloatVectorProperty, FloatProperty
from math import pi
import colorsys

def create_material(context, name, root):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    ntree = mat.node_tree
    outNode = ntree.get_output_node('octane')
    nodes = mat.node_tree.nodes
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

def assign_oclight(context, type):
    for obj in context.selected_objects:
        if('oc_light' not in obj):
            obj['oc_light'] = type

def get_bright_color(color):
    hsv_color = colorsys.rgb_to_hsv(color[0], color[1], color[2])
    return colorsys.hsv_to_rgb(hsv_color[0], hsv_color[1], 1.0) + (1.0,)

def update_sss(self, context):
    if(self.enable_geneate_transmission):
        self.sss_transmission = get_bright_color(self.sss_albedo)

def selected_mat_get(self):
    context = bpy.context
    if(context.active_object):
        if(context.active_object.active_material):
            return bpy.context.active_object.active_material.name
    return ''

def selected_mat_set(self, value):
    if(value!=''):
        assign_material(bpy.context, bpy.data.materials[value])

# Assign Materials
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

class OctaneAssignSSS(Operator):
    bl_label = 'SSS Material'
    bl_idname = 'octane.assign_sss'
    bl_options = {'REGISTER', 'UNDO'}
    
    sss_albedo: FloatVectorProperty(
        name="Albedo",
        default = (0.035, 0.062, 0.085, 1.0),
        size=4,
        min = 0,
        max = 1,
        subtype="COLOR",
        update=update_sss)
    
    sss_transmission: FloatVectorProperty(
        name="Transmission",
        default = get_bright_color((0.035, 0.062, 0.085, 1.0)),
        size=4,
        min = 0,
        max = 1,
        subtype="COLOR")
    
    sss_absorption: FloatVectorProperty(
        name="Absorption",
        default = (0, 0, 0, 1),
        size=4,
        min = 0,
        max = 1,
        subtype="COLOR")
    
    sss_scattering: FloatVectorProperty(
        name="Scattering",
        default = (0, 0, 0, 1),
        size=4,
        min = 0,
        max = 1,
        subtype="COLOR")

    sss_density: FloatProperty(
        name="Density",
        default=5.0,
        min=0.001,
        step=10, 
        precision=3)

    enable_geneate_transmission: BoolProperty(
        default=False,
        update=update_sss)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'sss_albedo', text='Albedo')
        col.prop(self, 'enable_geneate_transmission', text='Generate Transmission from Albedo')
        col = layout.column()
        col.enabled = (not self.enable_geneate_transmission)
        col.prop(self, 'sss_transmission', text='Transmission')
        col = layout.column()
        col.prop(self, 'sss_absorption', text='Absorption')
        col.prop(self, 'sss_scattering', text='Scattering')
        col.separator()
        col.prop(self, 'sss_density', text='Density')
    
    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Universal', 'ShaderNodeOctUniversalMat')
        nodes = mat.node_tree.nodes
        # Diffuse Color
        diffuseNode = nodes.new('ShaderNodeOctRGBSpectrumTex')
        diffuseNode.location = (-210, 300)
        diffuseNode.name = 'DiffuseColor'
        diffuseNode.inputs['Color'].default_value = self.sss_albedo
        # Transmission Color
        transmissionNode = nodes.new('ShaderNodeOctRGBSpectrumTex')
        transmissionNode.location = (-210, 400)
        transmissionNode.name = 'TransmissionColor'
        transmissionNode.inputs['Color'].default_value = self.sss_transmission
        # Scatter Medium
        scatterNode = nodes.new('ShaderNodeOctScatteringMedium')
        scatterNode.location = (-210, -500)
        scatterNode.name = 'ScatterMedium'
        scatterNode.inputs['Density'].default_value = self.sss_density
        scatterNode.inputs['Absorption Tex'].default_value = self.sss_absorption
        scatterNode.inputs['Scattering Tex'].default_value = self.sss_scattering
        # Connections
        mat.node_tree.links.new(scatterNode.outputs[0], nodes[1].inputs['Medium'])
        mat.node_tree.links.new(transmissionNode.outputs[0], nodes[1].inputs['Transmission'])
        mat.node_tree.links.new(diffuseNode.outputs[0], nodes[1].inputs['Albedo color'])
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

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
    
    light_type: EnumProperty(items=[
        ('None', 'None', ''),
        ('Point', 'Point', ''),
        ('Mesh', 'Mesh', ''),
        ('Area', 'Area', ''),
        ('Spot', 'Spot', ''),
        ('Toon', 'Toon', ''),
    ], name='Mark as', default='Mesh')

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
        assign_oclight(context, self.light_type)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneAssignColorgrid(Operator):
    bl_label = 'Color Grid Material'
    bl_idname = 'octane.assign_colorgrid'
    bl_options = {'REGISTER', 'UNDO'}

    resolutions: EnumProperty(items=[
        ('1024', '1024x1024', ''),
        ('2048', '2048x2048', ''),
        ('4096', '4096x4096', ''),
    ], name='Resolution', default='1024')

    def execute(self, context):
        imgName = 'COLOR_GRID_' + self.resolutions
        # Create material
        mat = create_material(context, 'OC_Colorgrid', 'ShaderNodeOctDiffuseMat')
        nodes = mat.node_tree.nodes
        imgNode = nodes.new('ShaderNodeOctImageTex')
        imgNode.location = (-210, 300)
        if(imgName not in bpy.data.images):
            img = bpy.data.images.new(imgName, int(self.resolutions), int(self.resolutions))
            img.generated_type = 'COLOR_GRID'
            imgNode.image = img
        else:
            imgNode.image = bpy.data.images[imgName]
        mat.node_tree.links.new(imgNode.outputs[0], nodes[1].inputs['Diffuse'])
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneAssignUVgrid(Operator):
    bl_label = 'UV Grid Material'
    bl_idname = 'octane.assign_uvgrid'
    bl_options = {'REGISTER', 'UNDO'}

    resolutions: EnumProperty(items=[
        ('1024', '1024x1024', ''),
        ('2048', '2048x2048', ''),
        ('4096', '4096x4096', ''),
    ], name='Resolution', default='1024')

    def execute(self, context):
        imgName = 'UV_GRID_' + self.resolutions
        # Create material
        mat = create_material(context, 'OC_UVgrid', 'ShaderNodeOctDiffuseMat')
        nodes = mat.node_tree.nodes
        imgNode = nodes.new('ShaderNodeOctImageTex')
        imgNode.location = (-210, 300)
        if(imgName not in bpy.data.images):
            img = bpy.data.images.new(imgName, int(self.resolutions), int(self.resolutions))
            img.generated_type = 'UV_GRID'
            imgNode.image = img
        else:
            imgNode.image = bpy.data.images[imgName]
        mat.node_tree.links.new(imgNode.outputs[0], nodes[1].inputs['Diffuse'])
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

# Rename, Copy and Paste materials
class OctaneRenameMat(Operator):
    bl_label = 'Rename'
    bl_idname = 'octane.rename_mat'
    bl_options = {'REGISTER', 'UNDO'}

    name: StringProperty(
        name='Name',
        default='Unknown'
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if(obj is not None):
            if(obj.type == 'MESH'):
                return (len(obj.material_slots)>=1)
        return False
    def execute(self, context):
        obj = context.active_object
        obj.active_material.name = self.name
        return {'FINISHED'}

    def invoke(self, context, event):
        self.name = context.active_object.active_material.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneCopyMat(Operator):
    bl_label = 'Copy'
    bl_idname = 'octane.copy_mat'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if(obj is not None):
            if(obj.type == 'MESH'):
                return (len(obj.material_slots)>=1)
        return False

    def execute(self, context):
        obj = context.active_object
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

# Autosmooth
class OctaneAutosmooth(Operator):
    bl_label = 'Mesh Autosmooth'
    bl_idname = 'octane.autosmooth'
    bl_options = {'REGISTER', 'UNDO'}

    autosmooth_value: IntProperty(default=0, min=-180, max=180, subtype='ANGLE', name='Value')

    def execute(self, context):
        for obj in context.selected_objects:
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = (pi * self.autosmooth_value / 180)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        if(context.active_object):
            if(context.active_object.type == 'MESH'):
                self.autosmooth_value = (context.active_object.data.auto_smooth_angle * 180 / pi)
        wm = context.window_manager
        return wm.invoke_props_dialog(self)