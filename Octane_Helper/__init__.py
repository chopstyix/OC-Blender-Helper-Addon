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
from bpy.types import Menu
from bpy.props import BoolProperty, StringProperty
from . icons import register_icons, unregister_icons, get_icon
from . operators import register_operators, unregister_operators, assign_material

bl_info = {
    "name": "Octane Helper",
    "description": "A helper addon for Octane Blender edition",
    "author": "Yichen Dou",
    "version": (1, 5, 0),
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
        layout.menu(OctaneMaterialsMenu.bl_idname, icon='MATSPHERE')
        layout.menu(OctaneEnvironmentMenu.bl_idname, icon='LIGHT_SUN')
        layout.menu(OctaneRenderMenu.bl_idname, icon='RESTRICT_RENDER_OFF')

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
        layout.label(text='Select a Material to apply')
        layout.prop_search(context.scene, property='selected_mat', search_data=bpy.data, search_property='materials', text='', icon='MATERIAL')
        layout.separator()
        layout.operator('octane.assign_universal', icon='NODE_MATERIAL')
        layout.operator('octane.assign_diffuse', icon='NODE_MATERIAL')
        layout.operator('octane.assign_glossy', icon='NODE_MATERIAL')
        layout.operator('octane.assign_specular', icon='NODE_MATERIAL')
        layout.operator('octane.assign_mix', icon='NODE_MATERIAL')
        layout.operator('octane.assign_portal', icon='NODE_MATERIAL')
        layout.operator('octane.assign_shadowcatcher', icon='NODE_MATERIAL')
        layout.operator('octane.assign_toon', icon='NODE_MATERIAL')
        layout.operator('octane.assign_metal', icon='NODE_MATERIAL')
        layout.operator('octane.assign_layered', icon='NODE_MATERIAL')
        layout.operator('octane.assign_composite', icon='NODE_MATERIAL')
        layout.operator('octane.assign_hair', icon='NODE_MATERIAL')
        layout.separator()
        layout.operator('octane.assign_emissive', icon='LIGHT')
        layout.operator('octane.assign_colorgrid', icon='LIGHTPROBE_GRID')
        layout.operator('octane.assign_uvgrid', icon='MESH_GRID')
        layout.separator()
        layout.operator('octane.copy_mat', icon='COPYDOWN')
        layout.operator('octane.paste_mat', icon='PASTEDOWN')
        layout.separator()
        layout.prop(context.scene, 'is_smooth')
        layout.operator('octane.autosmooth', icon='SMOOTHCURVE')

class OctaneEnvironmentMenu(Menu):
    bl_label = 'Environment'
    bl_idname = 'OCTANE_MT_environment'

    def draw(self, context):
        layout = self.layout
        layout.operator('octane.setup_hdri', text='Setup Texture Environment', icon='WORLD')
        layout.operator('octane.transform_hdri', icon='FILE_3D')
        layout.separator()
        layout.operator('octane.add_backplate', icon='ADD')
        layout.operator('octane.remove_backplate', icon='REMOVE')
        layout.operator('octane.modify_backplate', icon='MODIFIER_DATA')

class OctaneRenderMenu(Menu):
    bl_label = 'Render'
    bl_idname = 'OCTANE_MT_render'

    def draw(self, context):
        layout = self.layout
        layout.operator('octane.manage_imager', icon='IMAGE')
        layout.operator('octane.manage_postprocess', icon='CAMERA_STEREO')
        layout.operator('octane.manage_denoiser', icon='OUTLINER_OB_LIGHTPROBE')
        layout.operator('octane.manage_render_passes', icon='IMAGE_REFERENCE')
        layout.operator('octane.manage_render_layers', icon='RENDERLAYERS')
        layout.operator('octane.toggle_claymode', icon='SCULPTMODE_HLT')
        layout.separator()
        layout.operator('octane.set_renderid', icon='FILE_IMAGE')
        layout.separator()
        layout.operator('octane.open_compositor', icon='NODE_COMPOSITING')
        

# Register and Unregister
classes = (
    VIEW3D_MT_object_octane,
    VIEW3D_MT_edit_mesh_octane,
    OctaneMaterialsMenu,
    OctaneEnvironmentMenu,
    OctaneRenderMenu
)

def object_menu_func(self, context):
    if context.scene.render.engine == 'octane':
        self.layout.menu('VIEW3D_MT_object_octane', icon_value=get_icon('OCT_RENDER'))
        self.layout.separator()

def edit_menu_func(self, context):
    if context.scene.render.engine == 'octane':
        self.layout.menu('VIEW3D_MT_edit_mesh_octane', icon_value=get_icon('OCT_RENDER'))
        self.layout.separator()

def selected_mat_update(self, context):
    if(context.scene.selected_mat!=''):
        assign_material(context, bpy.data.materials[context.scene.selected_mat])
        context.scene.selected_mat = ''

def register():
    register_icons()
    register_operators()
    bpy.types.Material.copied_mat = None
    bpy.types.Scene.selected_mat = StringProperty(default='', update=selected_mat_update)
    bpy.types.Scene.is_smooth = BoolProperty(name='Always smooth materials', default=True)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object_context_menu.prepend(object_menu_func)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.prepend(edit_menu_func)

def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(edit_menu_func)
    bpy.types.VIEW3D_MT_object_context_menu.remove(object_menu_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    unregister_operators()
    unregister_icons()

if __name__ == "__main__":
    register()