import bpy, bmesh
from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty, BoolProperty, StringProperty, FloatVectorProperty, FloatProperty
from octane import converters
from math import pi
from .. assets import osl_dir
import colorsys
import os

def create_material(context, name, root):
    # Get pref settings
    prefs = context.preferences.addons['Octane_Helper'].preferences
    # Create a new material which contains a shader and output node by default
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    ntree = mat.node_tree
    outNode = ntree.get_output_node('octane')
    outNode.name = 'output'
    nodes = mat.node_tree.nodes
    # Get the default shader that is created automatically and remove it later
    oldMainMat = nodes[0]
    # Create a new shader node
    mainMat = nodes.new(root)
    mainMat.location = oldMainMat.location
    mainMat.name = 'root'
    if('Smooth' in mainMat.inputs):
        mainMat.inputs['Smooth'].default_value = context.scene.is_smooth
    if(hasattr(mainMat, 'brdf_model')):
        mainMat.brdf_model = prefs.brdf_model
    nodes.remove(oldMainMat)
    mat.node_tree.links.new(outNode.inputs['Surface'], mainMat.outputs[0])
    return mat

def assign_material(context, mat):
    # Object mode
    if(context.mode == 'OBJECT'):
        for obj in context.selected_objects:
            if(obj.type == 'MESH'):
                obj.active_material = mat
                obj.data.update()
    # Edit mode
    elif(context.mode == 'EDIT_MESH'):
        for obj in context.selected_objects:
            if(obj.type == 'MESH'):
                bm = bmesh.from_edit_mesh(obj.data)
                for face in bm.faces:
                    if face.select:
                        # If no base material found, create one
                        if (len(obj.material_slots)==0):
                            obj.active_material = create_material(context, mat.name + '_Base', 'ShaderNodeOctDiffuseMat')
                        if(obj.active_material != mat):
                            obj.data.materials.append(mat)
                        obj.active_material_index = len(obj.material_slots) - 1
                        face.material_index = len(obj.material_slots) - 1
                obj.data.update()

def assign_material_objs (objs, mat):
    for obj in objs:
        if(obj.type == 'MESH'):
            obj.active_material = mat
            obj.data.update()

def assign_oclight(context, type):
    for obj in context.selected_objects:
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

def convert_mat_octane(obj):
    slots = obj.material_slots
    for slot in slots:
        mat = slot.material
        if(mat):
            # Get the output node and determine its type. If its not octane type, convert it
            outNode = mat.node_tree.get_output_node('octane')
            if(outNode and outNode.target != 'octane'):
                converted_material = mat.copy()
                converted_material.name = mat.name
                converters.convert_to_octane_material(mat, converted_material)
                converters.convert_all_related_material(mat, converted_material)
                slot.material = converted_material

# Assign material
class OctaneAssignUniversal(Operator):
    bl_label = 'Universal Material'
    bl_idname = 'octane.assign_universal'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Universal', 'ShaderNodeOctUniversalMat')
        # Assign material to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignGlossy(Operator):
    bl_label = 'Glossy Material'
    bl_idname = 'octane.assign_glossy'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Glossy', 'ShaderNodeOctGlossyMat')
        # Assign material to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignSpecular(Operator):
    bl_label = 'Specular Material'
    bl_idname = 'octane.assign_specular'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Specular', 'ShaderNodeOctSpecularMat')
        # Assign material to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignDiffuse(Operator):
    bl_label = 'Diffuse Material'
    bl_idname = 'octane.assign_diffuse'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Diffuse', 'ShaderNodeOctDiffuseMat')
        # Assign material to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignMix(Operator):
    bl_label = 'Mix Material'
    bl_idname = 'octane.assign_mix'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Mix', 'ShaderNodeOctMixMat')
        # Assign material to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignPortal(Operator):
    bl_label = 'Portal Material'
    bl_idname = 'octane.assign_portal'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Portal', 'ShaderNodeOctPortalMat')
        # Assign material to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignShadowCatcher(Operator):
    bl_label = 'ShadowCatcher Material'
    bl_idname = 'octane.assign_shadowcatcher'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_ShadowCatcher', 'ShaderNodeOctShadowCatcherMat')
        # Assign material to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignToon(Operator):
    bl_label = 'Toon Material'
    bl_idname = 'octane.assign_toon'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Toon', 'ShaderNodeOctToonMat')
        # Assign material to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignMetal(Operator):
    bl_label = 'Metal Material'
    bl_idname = 'octane.assign_metal'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Metal', 'ShaderNodeOctMetalMat')
        # Assign material to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignLayered(Operator):
    bl_label = 'Layered Material'
    bl_idname = 'octane.assign_layered'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Layered', 'ShaderNodeOctLayeredMat')
        # Assign material to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignComposite(Operator):
    bl_label = 'Composite Material'
    bl_idname = 'octane.assign_composite'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Composite', 'ShaderNodeOctCompositeMat')
        # Assign material to selected
        assign_material(context, mat)
        return {'FINISHED'}

class OctaneAssignHair(Operator):
    bl_label = 'Hair Material'
    bl_idname = 'octane.assign_hair'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Hair', 'ShaderNodeOctHairMat')
        # Assign material to selected
        assign_material(context, mat)
        return {'FINISHED'}

# Special materials
class OCtaneAssignClearGlass(Operator):
    bl_label = 'Clear Glass Material'
    bl_idname = 'octane.assign_clear_glass'
    bl_options = {'REGISTER', 'UNDO'}

    roughness: FloatProperty(
        name='Roughness',
        default=0.063,
        min=0.0,
        max=1.0,
        step=10, 
        precision=3
    )

    index: FloatProperty(
        name="Index",
        default=1.45,
        min=1,
        max=8,
        step=10, 
        precision=3
    )

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_ClearGlass', 'ShaderNodeOctSpecularMat')
        nodes = mat.node_tree.nodes
        nodes[1].inputs['Roughness'].default_value = self.roughness
        nodes[1].inputs['Index'].default_value = self.index
        osl_node = nodes.new('ShaderNodeOctOSLTex')
        osl_node.location = (-210, 30)
        osl_node.mode = 'EXTERNAL'
        osl_node.filepath = os.path.join(osl_dir, 'clear_glass.osl')
        mat.node_tree.links.new(osl_node.outputs[0], nodes[1].inputs['Opacity'])
        # Assign material to selected
        assign_material(context, mat)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

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
        mat = create_material(context, 'OC_SSS', 'ShaderNodeOctUniversalMat')
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
        # Assign material to selected
        assign_material(context, mat)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneAssignEmission(Operator):
    bl_label = 'Setup'
    bl_idname = 'octane.assign_emission'
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.hdr;*.png;*.jpeg;*.jpg;*.exr", options={"HIDDEN"})

    emission_type: StringProperty(default='RGB')

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
    
    emission_double: BoolProperty(
        name="Double Sided",
        default=False)
    
    light_type: EnumProperty(items=[
        ('None', 'None', ''),
        ('Mesh', 'Mesh', ''),
        ('Sphere', 'Sphere', ''),
        ('Area', 'Area', ''),
        ('Spot', 'Spot', ''),
        ('Point Toon', 'Point Toon', ''),
        ('Directional Toon', 'Directional Toon', '')
    ], name='Mark as', default='Mesh') 

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        if(self.emission_type=='RGB' or self.emission_type=='IES'):
            col.prop(self, 'rgb_emission_color')
        col.prop(self, 'emission_power')
        col.prop(self, 'emission_surface_brightness')
        col.prop(self, 'emission_double')
        col.prop(self, 'light_type')

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Emissive', 'ShaderNodeOctDiffuseMat')
        nodes = mat.node_tree.nodes

        # Since this operator supports 3 different types of emission, we need to handle them seperately
        if(self.emission_type == 'RGB'):
            emissionNode = nodes.new('ShaderNodeOctBlackBodyEmission')
            emissionNode.location = (-210, 300)
            emissionNode.inputs['Power'].default_value = self.emission_power
            emissionNode.inputs['Surface brightness'].default_value = self.emission_surface_brightness
            rgbNode = nodes.new('ShaderNodeOctRGBSpectrumTex')
            rgbNode.location = (-410, 300)
            rgbNode.inputs['Color'].default_value = self.rgb_emission_color
            mat.node_tree.links.new(rgbNode.outputs[0], emissionNode.inputs['Texture'])
            mat.node_tree.links.new(emissionNode.outputs[0], nodes[1].inputs['Emission'])
        elif(self.emission_type == 'TEX'):
            emissionNode = nodes.new('ShaderNodeOctTextureEmission')
            emissionNode.location = (-210, 300)
            emissionNode.inputs['Power'].default_value = self.emission_power
            emissionNode.inputs['Surface brightness'].default_value = self.emission_surface_brightness
            imgNode = nodes.new('ShaderNodeOctImageTex')
            imgNode.location = (-460, 300)
            imgNode.image = bpy.data.images.load(self.filepath)
            mat.node_tree.links.new(imgNode.outputs[0], emissionNode.inputs['Texture'])
            mat.node_tree.links.new(emissionNode.outputs[0], nodes[1].inputs['Emission'])
        elif(self.emission_type == 'IES'):
            emissionNode = nodes.new('ShaderNodeOctBlackBodyEmission')
            emissionNode.location = (-210, 300)
            emissionNode.inputs['Power'].default_value = self.emission_power
            emissionNode.inputs['Surface brightness'].default_value = self.emission_surface_brightness
            emissionNode.inputs['Double-sided'].default_value = self.emission_double
            rgbNode = nodes.new('ShaderNodeOctRGBSpectrumTex')
            rgbNode.location = (-410, 400)
            rgbNode.inputs['Color'].default_value = self.rgb_emission_color
            imgNode = nodes.new('ShaderNodeOctImageTex')
            imgNode.location = (-460, 300)
            imgNode.image = bpy.data.images.load(self.filepath)
            projectNode = nodes.new('ShaderNodeOctPerspProjection')
            projectNode.location = (-660, 250)
            projectNode.coordinate_space_mode = 'OCT_POSITION_NORMAL'
            mat.node_tree.links.new(projectNode.outputs[0], imgNode.inputs['Projection'])
            mat.node_tree.links.new(rgbNode.outputs[0], emissionNode.inputs['Texture'])
            mat.node_tree.links.new(imgNode.outputs[0], emissionNode.inputs['Distribution'])
            mat.node_tree.links.new(emissionNode.outputs[0], nodes[1].inputs['Emission'])

        # Assign material to selected
        assign_material(context, mat)
        assign_oclight(context, self.light_type)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        if(self.emission_type == 'RGB'):
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
        elif(self.emission_type == 'TEX'):
            context.window_manager.fileselect_add(self)
            return {"RUNNING_MODAL"}
        elif(self.emission_type == 'IES'):
            context.window_manager.fileselect_add(self)
            return {"RUNNING_MODAL"}

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
        # Assign material to selected
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
        # Assign material to selected
        assign_material(context, mat)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneAssignPattern(Operator):
    bl_label = 'Setup'
    bl_idname = 'octane.assign_pattern'
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.hdr;*.png;*.jpeg;*.jpg;*.exr", options={"HIDDEN"})

    material_type: EnumProperty(items=[
        ('Diffuse', 'Diffuse', ''),
        ('Universal', 'Universal', '')
    ], default='Diffuse')
    generate_subdiv: BoolProperty(name='Subdivision Modifier', default=False)
    generate_shrinkwrap: BoolProperty(name='Shrinkwrap Modifier', default=False)
    generate_displace: BoolProperty(name='Displace Modifier', default=False)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, 'material_type', text='')
        col.prop(self, 'generate_subdiv')
        col.prop(self, 'generate_shrinkwrap')
        col.prop(self, 'generate_displace')
    
    def execute(self, context):
        if(self.filepath != ''):
            # Create material
            mat = create_material(context, 'OC_Pattern', 'ShaderNodeOctMixMat')
            nodes = mat.node_tree.nodes
            if(self.material_type == 'Diffuse'):
                baseNode = nodes.new('ShaderNodeOctDiffuseMat')
            else:
                baseNode = nodes.new('ShaderNodeOctUniversalMat')
            baseNode.location = (-210, 50)
            baseNode.inputs['Smooth'].default_value = context.scene.is_smooth
            transparentNode = nodes.new('ShaderNodeOctDiffuseMat')
            transparentNode.location = (10, 50)
            transparentNode.inputs['Opacity'].default_value = 0.0
            alphaImgNode = nodes.new('ShaderNodeOctAlphaImageTex')
            alphaImgNode.location = (-460, 600)
            alphaImgNode.image = bpy.data.images.load(self.filepath)
            imgNode = nodes.new('ShaderNodeOctImageTex')
            imgNode.location = (-460, 300)
            imgNode.image = alphaImgNode.image
            # Link nodes
            if(self.material_type == 'Diffuse'):
                mat.node_tree.links.new(imgNode.outputs[0], baseNode.inputs['Diffuse'])
            else:
                mat.node_tree.links.new(imgNode.outputs[0], baseNode.inputs['Albedo color'])
            mat.node_tree.links.new(alphaImgNode.outputs[0], nodes[1].inputs['Amount'])
            mat.node_tree.links.new(baseNode.outputs[0], nodes[1].inputs['Material1'])
            mat.node_tree.links.new(transparentNode.outputs[0], nodes[1].inputs['Material2'])
            # Assign material to selected
            assign_material(context, mat)
            # Add modifiers
            if(self.generate_subdiv):
                bpy.ops.object.modifier_add(type='SUBSURF')
                context.active_object.modifiers["Subdivision"].subdivision_type = 'SIMPLE'
                context.active_object.modifiers["Subdivision"].levels = 6
                context.active_object.modifiers["Subdivision"].render_levels = 6
            if(self.generate_shrinkwrap):
                bpy.ops.object.modifier_add(type='SHRINKWRAP')
                context.active_object.modifiers['Shrinkwrap'].wrap_method = 'PROJECT'
            if(self.generate_displace):
                bpy.ops.object.modifier_add(type='DISPLACE')
                context.active_object.modifiers["Displace"].mid_level = 0
                context.active_object.modifiers["Displace"].strength = 0.001
            if(self.generate_subdiv or self.generate_shrinkwrap or self.generate_displace):
                bpy.ops.object.make_links_data(type='MODIFIERS')

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

class OctaneAssignMantaflowVolume(Operator):
    bl_label = 'Mantaflow Volume Material'
    bl_idname = 'octane.assign_mantaflow_volume'
    bl_options = {'REGISTER', 'UNDO'}

    mat_type: EnumProperty(items=[
        ('Fire', 'Fire + Smoke', ''),
        ('Smoke', 'Smoke', '')
    ], default='Fire')

    smoke_color: FloatVectorProperty(
        name="Smoke Color",
        default = (0.129468, 0.129468, 0.129468, 1.000000),
        size=4,
        min = 0,
        max = 1,
        subtype="COLOR")

    fire_color: FloatVectorProperty(
        name="Fire Color",
        default = (1.000000, 0.261137, 0.056232, 1.000000),
        size=4,
        min = 0,
        max = 1,
        subtype="COLOR")

    fire_power: FloatProperty(
        name="Power", 
        default=100, 
        min=0.001,
        step=10, 
        precision=3)

    density: FloatProperty(
        name="Density", 
        default=8, 
        min=0.001,
        step=10, 
        precision=3)
    
    details: FloatProperty(
        name="Details", 
        default=0.2, 
        min=0.001,
        step=10, 
        precision=3)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'mat_type', text='')
        col = layout.column(align=True)
        col.prop(self, 'smoke_color')
        if(self.mat_type == 'Fire'):
            col.prop(self, 'fire_color')
            col.prop(self, 'fire_power')
        col = layout.column(align=True)
        col.prop(self, 'density')
        col.prop(self, 'details')

    def execute(self, context):
        # Create material
        if(self.mat_type == 'Fire'):
            mat = create_material(context, 'OC_Mantaflow_Fire', 'ShaderNodeOctVolumeMedium')
        else:
            mat = create_material(context, 'OC_Mantaflow_Smoke', 'ShaderNodeOctVolumeMedium')
        nodes = mat.node_tree.nodes

        # Set default values for root shader
        nodes[1].inputs['Density'].default_value = self.density
        nodes[1].inputs['Vol. step length'].default_value = self.details
        nodes[1].inputs['Absorption Tex'].default_value = self.smoke_color
        nodes[1].inputs['Scattering Tex'].default_value = (1.000000, 1.000000, 1.000000, 1.000000)

        # Abs ramp node
        absRampNode = nodes.new('ShaderNodeOctVolumeRampTex')
        absColor1 = absRampNode.color_ramp.elements[0]
        absColor1.color = (1.0, 1.0, 1.0, 1.0)
        absColor1.position = 0.393
        absColor2 = absRampNode.color_ramp.elements[1]
        absColor2.color = (0.0, 0.0, 0.0, 1.0)
        absColor2.position = 0.671
        absRampNode.inputs['Max grid val.'].default_value = 1.0
        absRampNode.location = (-210, 400)

        # Scatter ramp node
        sctRampNode = nodes.new('ShaderNodeOctVolumeRampTex')
        sctColor1 = sctRampNode.color_ramp.elements[0]
        sctColor1.position = 0.407
        sctColor2 = sctRampNode.color_ramp.elements[1]
        sctColor2.position = 1.0
        sctRampNode.inputs['Max grid val.'].default_value = 1.0
        sctRampNode.location = (-210, 200)

        # Connect abs and scatter ramps to root shader node
        mat.node_tree.links.new(absRampNode.outputs[0], nodes[1].inputs['Abs. ramp'])
        mat.node_tree.links.new(sctRampNode.outputs[0], nodes[1].inputs['Scat. ramp'])

        # Add emission if it's a fire
        if(self.mat_type == 'Fire'):
            emissionRampNode = nodes.new('ShaderNodeOctVolumeRampTex') 
            emissionColor1 = emissionRampNode.color_ramp.elements[0]
            emissionColor1.position = 0
            emissionColor2 = emissionRampNode.color_ramp.elements[1]
            emissionColor2.color = self.fire_color
            emissionColor2.position = 0.550
            emissionRampNode.inputs['Max grid val.'].default_value = 8.0
            emissionRampNode.color_ramp.octane_interpolation_type = 'OCTANE_INTERPOLATION_CUBIC'
            emissionRampNode.location = (-210, 0)

            emissionNode = nodes.new('ShaderNodeOctTextureEmission')
            emissionNode.inputs['Power'].default_value = self.fire_power
            emissionNode.location = (-210, -200)

            mat.node_tree.links.new(emissionRampNode.outputs[0], nodes[1].inputs['Emiss. ramp'])
            mat.node_tree.links.new(emissionNode.outputs[0], nodes[1].inputs['Emission'])
        
        # Assign material to selected
        assign_material(context, mat)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneAssignEmbergenVolume(Operator):
    bl_label = 'Embergen Volume Material'
    bl_idname = 'octane.assign_embergen_volume'
    bl_options = {'REGISTER', 'UNDO'}

    volume_type: EnumProperty(items=[
        ('Temperature', 'Temperature', '')
    ], default='Temperature')

    smoke_color: FloatVectorProperty(
        name="Smoke Color",
        default = (0.478368, 0.478368, 0.478368, 1.000000),
        size=4,
        min = 0,
        max = 1,
        subtype="COLOR")

    fire_color: FloatVectorProperty(
        name="Fire Color",
        default = (1.000000, 0.276358, 0.086804, 1.000000),
        size=4,
        min = 0,
        max = 1,
        subtype="COLOR")

    fire_power: FloatProperty(
        name="Power", 
        default=50, 
        min=0.001,
        step=10, 
        precision=3)

    density: FloatProperty(
        name="Density", 
        default=2, 
        min=0.001,
        step=10, 
        precision=3)
    
    details: FloatProperty(
        name="Details", 
        default=2, 
        min=0.001,
        step=10, 
        precision=3)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'volume_type', text='')
        col = layout.column(align=True)
        col.prop(self, 'smoke_color')
        col.prop(self, 'fire_color')
        col.prop(self, 'fire_power')
        col = layout.column(align=True)
        col.prop(self, 'density')
        col.prop(self, 'details')

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Embergen_Temperature', 'ShaderNodeOctVolumeMedium')
        nodes = mat.node_tree.nodes

        # Set default values for root shader
        nodes[1].inputs['Density'].default_value = self.density
        nodes[1].inputs['Vol. step length'].default_value = self.details
        nodes[1].inputs['Absorption Tex'].default_value = self.smoke_color
        nodes[1].inputs['Scattering Tex'].default_value = (1.000000, 1.000000, 1.000000, 1.000000)

        # Abs ramp node
        absRampNode = nodes.new('ShaderNodeOctVolumeRampTex')
        absRampNode.color_ramp.octane_interpolation_type = 'OCTANE_INTERPOLATION_CUBIC'
        absColor1 = absRampNode.color_ramp.elements[0]
        absColor1.color = (0.0, 0.0, 0.0, 1.0)
        absColor1.position = 0.0
        absColor2 = absRampNode.color_ramp.elements[1]
        absColor2.color = (1.0, 1.0, 1.0, 1.0)
        absColor2.position = 0.571
        absRampNode.inputs['Max grid val.'].default_value = 2.0
        absRampNode.location = (-210, 400)

        # Scatter ramp node
        sctRampNode = nodes.new('ShaderNodeOctVolumeRampTex')
        sctRampNode.color_ramp.octane_interpolation_type = 'OCTANE_INTERPOLATION_CUBIC'
        sctColor1 = sctRampNode.color_ramp.elements[0]
        sctColor1.position = 0.0
        sctColor2 = sctRampNode.color_ramp.elements[1]
        sctColor2.position = 0.371
        sctRampNode.inputs['Max grid val.'].default_value = 5.0
        sctRampNode.location = (-210, 200)

        # Emission ramp node
        emissionRampNode = nodes.new('ShaderNodeOctVolumeRampTex') 
        emissionColor1 = emissionRampNode.color_ramp.elements[0]
        emissionColor1.position = 0.366102
        emissionColor2 = emissionRampNode.color_ramp.elements[1]
        emissionColor2.color = self.fire_color
        emissionColor2.position = 0.875
        emissionRampNode.inputs['Max grid val.'].default_value = 5000.0
        emissionRampNode.location = (-210, 0)

        # Emission node
        emissionNode = nodes.new('ShaderNodeOctBlackBodyEmission')
        emissionNode.inputs['Power'].default_value = self.fire_power
        emissionNode.inputs['Surface brightness'].default_value = True
        emissionNode.location = (-210, -200)

        # Link nodes
        mat.node_tree.links.new(absRampNode.outputs[0], nodes[1].inputs['Abs. ramp'])
        mat.node_tree.links.new(sctRampNode.outputs[0], nodes[1].inputs['Scat. ramp'])
        mat.node_tree.links.new(emissionRampNode.outputs[0], nodes[1].inputs['Emiss. ramp'])
        mat.node_tree.links.new(emissionNode.outputs[0], nodes[1].inputs['Emission'])
        
        # Assign material to selected
        assign_material(context, mat)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

# Rename, Copy and Paste materials
class OctaneRenameMat(Operator):
    bl_label = 'Rename'
    bl_idname = 'octane.rename_mat'
    bl_description = 'Rename the active material'
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
    bl_description = 'Copy active material of the selected object to paste it later'
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
    bl_description = 'Paste the copied material to all selected objects/faces'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (bpy.types.Material.copied_mat is not None)
    def execute(self, context):
        if(bpy.types.Material.copied_mat):
            assign_material(context, bpy.types.Material.copied_mat)
        return {'FINISHED'}

class OctaneDuplicateMat(Operator):
    bl_label = 'Duplicate'
    bl_idname = 'octane.duplicate_mat'
    bl_description = 'Duplicate the active material and copy it so you can paste it to other object/faces'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if(obj is not None):
            if(obj.type == 'MESH'):
                return (len(obj.material_slots)>=1)
        return False
    def execute(self, context):
        mat = context.active_object.active_material.copy()
        bpy.types.Material.copied_mat = mat
        return {'FINISHED'}

# Autosmooth
class OctaneAutosmooth(Operator):
    bl_label = 'Mesh Autosmooth'
    bl_idname = 'octane.autosmooth'
    bl_description = 'Blender autosmooth function'
    bl_options = {'REGISTER', 'UNDO'}

    enable_autosmooth: BoolProperty(default=True, name='Enable Autosmooth')
    autosmooth_value: IntProperty(default=0, min=-180, max=180, subtype='ANGLE', name='Angle')

    @classmethod
    def poll(cls, context):
        if(context.active_object):
            if(context.active_object.type == 'MESH'):
                return True
        return False

    def execute(self, context):
        for obj in context.selected_objects:
            obj.data.use_auto_smooth = self.enable_autosmooth
            obj.data.auto_smooth_angle = (pi * self.autosmooth_value / 180)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        self.enable_autosmooth = True
        self.autosmooth_value = (context.active_object.data.auto_smooth_angle * 180 / pi)
        return self.execute(context)

class OctaneConvertMat(Operator):
    bl_label = 'Blender Materials to Octane'
    bl_idname = 'octane.convert_mat'
    bl_description = 'Convert Cycles/EEVEE materials of selected objects to Octane materials using built-in Materials Converter (Dev)'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            if(obj.type == 'MESH'):
                convert_mat_octane(obj)
                obj.data.update()
        self.report({'INFO'}, 'Conversion finished')
        return {'FINISHED'}