# Octane Blender Helper Add-on
# Copyright (C) 2020 Yichen Dou
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.types import Operator, Menu
from bpy.props import IntProperty, EnumProperty, BoolProperty, StringProperty
import bmesh

bl_info = {
    "name": "Octane Helper",
    "description": "A helper addon for Octane Blender edition",
    "author": "Yichen Dou",
    "version": (1, 0, 0),
    "blender": (2, 81, 0),
    "warning": "",
    "wiki_url": "https://github.com/Yichen-Dou/OC-Blender-Helper-Addon",
    "support": "COMMUNITY",
    "category": "3D View"
}

# Main Octane menu
class VIEW3D_MT_object_octane(Menu):
    bl_label = 'Octane'

    def draw(self, context):
        layout = self.layout
        layout.menu(OctaneMaterialsMenu.bl_idname)
        layout.menu(OctaneEnvironmentMenu.bl_idname)
        layout.menu(OctaneLayersMenu.bl_idname)

class VIEW3D_MT_edit_mesh_octane(Menu):
    bl_label = 'Octane'

    def draw(self, context):
        layout = self.layout
        layout.menu(OctaneMaterialsMenu.bl_idname)

# Sub Octane menus
class OctaneMaterialsMenu(Menu):
    bl_label = 'Materials'
    bl_idname = 'OCTANE_MT_materials'

    def draw(self, context):
        layout = self.layout
        layout.operator(OctaneAssignUniversal.bl_idname)
        layout.operator(OctaneAssignDiffuse.bl_idname)
        layout.operator(OctaneAssignEmissive.bl_idname)
        layout.operator(OctaneAssignGlossy.bl_idname)
        layout.operator(OctaneAssignSpecular.bl_idname)
        layout.operator(OctaneAssignMix.bl_idname)
        layout.operator(OctaneAssignPortal.bl_idname)
        layout.operator(OctaneAssignShadowCatcher.bl_idname)
        layout.operator(OctaneAssignToon.bl_idname)
        layout.operator(OctaneAssignMetal.bl_idname)
        layout.operator(OctaneAssignLayered.bl_idname)
        layout.operator(OctaneAssignComposite.bl_idname)
        layout.operator(OctaneAssignHair.bl_idname)

class OctaneEnvironmentMenu(Menu):
    bl_label = 'Environment'
    bl_idname = 'OCTANE_MT_environment'

    def draw(self, context):
        layout = self.layout
        layout.operator(OctaneSetupHDRIEnv.bl_idname, text='Setup HDRI Environment')

class OctaneLayersMenu(Menu):
    bl_label = 'Layers'
    bl_idname = 'OCTANE_MT_layers'

    def draw(self, context):
        layout = self.layout
        layout.operator(OctaneSetRenderID.bl_idname)

# Octane operators
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

    def execute(self, context):
        # Create material
        mat = create_material(context, 'OC_Diffuse', 'ShaderNodeOctDiffuseMat')
        nodes = mat.node_tree.nodes
        emissionNode = nodes.new('ShaderNodeOctBlackBodyEmission')
        emissionNode.location = (-210, 300)
        emissionNode.inputs['Surface brightness'].default_value = True
        rgbNode = nodes.new('ShaderNodeOctRGBSpectrumTex')
        rgbNode.location = (-410, 300)
        rgbNode.inputs['Color'].default_value = (1, 1, 1, 1)
        mat.node_tree.links.new(rgbNode.outputs[0], emissionNode.inputs['Texture'])
        mat.node_tree.links.new(emissionNode.outputs[0], nodes[1].inputs['Emission'])
        # Assign materials to selected
        assign_material(context, mat)
        return {'FINISHED'}

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

class OctaneSetupHDRIEnv(Operator):
    bl_label = 'Setup'
    bl_idname = 'octane.setup_hdri'
    bl_options = {'REGISTER', 'UNDO'}

    filepath = StringProperty(subtype="FILE_PATH")
    filter_glob = StringProperty(default="*.hdr;*.png;*.jpeg;*.jpg;*.exr", options={"HIDDEN"})

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
            world.node_tree.links.new(transNode.outputs[0], sphereNode.inputs['Sphere Transformation'])
            world.node_tree.links.new(sphereNode.outputs[0], imgNode.inputs['Projection'])
            world.node_tree.links.new(imgNode.outputs[0], nodes[1].inputs['Texture'])
            context.scene.world = world
            # Setting up the octane
            context.scene.display_settings.display_device = 'None'
            context.scene.view_settings.exposure = 0
            context.scene.view_settings.gamma = 1
            context.scene.octane.hdr_tonemap_preview_enable = True
            context.scene.octane.use_preview_setting_for_camera_imager = True

        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

class OctaneSetRenderID(Operator):
    bl_label = 'Set Render Layer ID'
    bl_idname = 'octane.set_renderid'
    bl_options = {'REGISTER', 'UNDO'}

    rid = IntProperty(
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

# Helper methods
def create_material(context, name, root):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    outNode = nodes[0]
    oldMainMat = nodes[1]
    mainMat = nodes.new(root)
    mainMat.location = oldMainMat.location
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
    
# Register and Unregister
classes = (
    VIEW3D_MT_object_octane,
    VIEW3D_MT_edit_mesh_octane,
    OctaneMaterialsMenu,
    OctaneEnvironmentMenu,
    OctaneLayersMenu,
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
    OctaneSetupHDRIEnv,
    OctaneSetRenderID
)

def object_menu_func(self, context):
    if context.scene.render.engine == 'octane':
        self.layout.menu('VIEW3D_MT_object_octane')
        self.layout.separator()

def edit_menu_func(self, context):
    if context.scene.render.engine == 'octane':
        self.layout.menu('VIEW3D_MT_edit_mesh_octane')
        self.layout.separator()

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object_context_menu.prepend(object_menu_func)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.prepend(edit_menu_func)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_object_context_menu.remove(object_menu_func)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(edit_menu_func)

if __name__ == "__main__":
    register()