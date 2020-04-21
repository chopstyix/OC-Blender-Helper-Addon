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
from bpy.props import IntProperty, EnumProperty, BoolProperty
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


class VIEW3D_MT_edit_mesh_octane(Menu):
    bl_label = 'Octane'

    def draw(self, context):
        layout = self.layout
        layout.menu(OctaneMaterialsMenu.bl_idname)

# Sub Octane menus
class OctaneMaterialsMenu(Menu):
    bl_label = 'Materials'
    bl_idname = 'view3d.octane_materials'

    def draw(self, context):
        layout = self.layout
        layout.operator(OctaneAssignUniversal.bl_idname)
        layout.operator(OctaneAssignDiffuse.bl_idname)
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

# Octane operators
class OctaneAssignUniversal(Operator):
    bl_label = 'Universal Material'
    bl_idname = 'octane.assign_universal'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        assign_material('OC_Universal', 'ShaderNodeOctUniversalMat', context)
        return {'FINISHED'}

class OctaneAssignDiffuse(Operator):
    bl_label = 'Diffuse Material'
    bl_idname = 'octane.assign_diffuse'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        assign_material('OC_Diffuse', 'ShaderNodeOctDiffuseMat', context)
        return {'FINISHED'}

class OctaneAssignGlossy(Operator):
    bl_label = 'Glossy Material'
    bl_idname = 'octane.assign_glossy'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        assign_material('OC_Glossy', 'ShaderNodeOctGlossyMat', context)
        return {'FINISHED'}

class OctaneAssignSpecular(Operator):
    bl_label = 'Specular Material'
    bl_idname = 'octane.assign_specular'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        assign_material('OC_Specular', 'ShaderNodeOctSpecularMat', context)
        return {'FINISHED'}

class OctaneAssignMix(Operator):
    bl_label = 'Mix Material'
    bl_idname = 'octane.assign_mix'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        assign_material('OC_Mix', 'ShaderNodeOctMixMat', context)
        return {'FINISHED'}

class OctaneAssignPortal(Operator):
    bl_label = 'Portal Material'
    bl_idname = 'octane.assign_portal'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        assign_material('OC_Portal', 'ShaderNodeOctPortalMat', context)
        return {'FINISHED'}

class OctaneAssignShadowCatcher(Operator):
    bl_label = 'ShadowCatcher Material'
    bl_idname = 'octane.assign_shadowcatcher'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        assign_material('OC_ShadowCatcher', 'ShaderNodeOctShadowCatcherMat', context)
        return {'FINISHED'}

class OctaneAssignToon(Operator):
    bl_label = 'Toon Material'
    bl_idname = 'octane.assign_toon'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        assign_material('OC_Toon', 'ShaderNodeOctToonMat', context)
        return {'FINISHED'}

class OctaneAssignMetal(Operator):
    bl_label = 'Metal Material'
    bl_idname = 'octane.assign_metal'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        assign_material('OC_Metal', 'ShaderNodeOctMetalMat', context)
        return {'FINISHED'}

class OctaneAssignLayered(Operator):
    bl_label = 'Layered Material'
    bl_idname = 'octane.assign_layered'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        assign_material('OC_Layered', 'ShaderNodeOctLayeredMat', context)
        return {'FINISHED'}

class OctaneAssignComposite(Operator):
    bl_label = 'Composite Material'
    bl_idname = 'octane.assign_composite'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        assign_material('OC_Composite', 'ShaderNodeOctCompositeMat', context)
        return {'FINISHED'}

class OctaneAssignHair(Operator):
    bl_label = 'Hair Material'
    bl_idname = 'octane.assign_hair'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        assign_material('OC_Hair', 'ShaderNodeOctHairMat', context)
        return {'FINISHED'}

# Helper methods
def create_material(name, type):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    outNode = nodes[0]
    oldMainMat = nodes[1]
    mainMat = nodes.new(type)
    mainMat.location = oldMainMat.location
    nodes.remove(oldMainMat)
    mat.node_tree.links.new(outNode.inputs['Surface'], mainMat.outputs[0])
    return mat

def assign_material(name, type, context):
    mat = create_material(name, type)
    if(context.mode == 'OBJECT'):
        for obj in context.selected_objects:
            if(obj.type == 'MESH'):
                obj.active_material = mat
    elif(context.mode == 'EDIT_MESH'):
        for obj in context.selected_objects:
            if(obj.type == 'MESH'):
                bm = bmesh.from_edit_mesh(obj.data)
                for face in bm.faces:
                    if face.select:
                        if (len(obj.material_slots)==0):
                            obj.active_material = create_material(name + '_Base', type)
                        obj.data.materials.append(mat)
                        obj.active_material_index = len(obj.material_slots) - 1
                        face.material_index = len(obj.material_slots) - 1
                obj.data.update()

# Register and Unregister
classes = (
    VIEW3D_MT_object_octane,
    VIEW3D_MT_edit_mesh_octane,
    OctaneMaterialsMenu,
    OctaneAssignUniversal,
    OctaneAssignDiffuse,
    OctaneAssignGlossy,
    OctaneAssignSpecular,
    OctaneAssignMix,
    OctaneAssignPortal,
    OctaneAssignShadowCatcher,
    OctaneAssignToon,
    OctaneAssignMetal,
    OctaneAssignLayered,
    OctaneAssignComposite,
    OctaneAssignHair
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