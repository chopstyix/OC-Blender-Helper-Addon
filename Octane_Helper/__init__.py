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
from bpy.types import PropertyGroup, Menu, UIList
from bpy.props import BoolProperty, StringProperty, IntProperty, CollectionProperty, PointerProperty, EnumProperty
from . icons import register_icons, unregister_icons, get_icon
from . operators import register_operators, unregister_operators, assign_material

bl_info = {
    "name": "Octane Helper",
    "description": "A helper addon for Octane Blender edition",
    "author": "Yichen Dou",
    "version": (1, 8, 0),
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
        layout.menu(OctaneInfoMenu.bl_idname, icon='QUESTION')

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
        layout.operator('octane.assign_sss', icon='RADIOBUT_ON')
        layout.operator('octane.assign_emissive', icon='LIGHT')
        layout.operator('octane.assign_colorgrid', icon='LIGHTPROBE_GRID')
        layout.operator('octane.assign_uvgrid', icon='MESH_GRID')
        layout.separator()
        layout.operator('octane.rename_mat', icon='GREASEPENCIL')
        layout.operator('octane.copy_mat', icon='COPYDOWN')
        layout.operator('octane.paste_mat', icon='PASTEDOWN')
        if(bpy.types.Material.copied_mat!=None):
            layout.label(text='['+((bpy.types.Material.copied_mat.name[:16] + '..') if len(bpy.types.Material.copied_mat.name) > 16 else bpy.types.Material.copied_mat.name)+']')
        layout.separator()
        layout.prop(context.scene, 'is_smooth')
        layout.operator('octane.autosmooth', icon='SMOOTHCURVE')

class OctaneEnvironmentMenu(Menu):
    bl_label = 'Environment'
    bl_idname = 'OCTANE_MT_environment'

    def draw(self, context):
        layout = self.layout
        layout.operator('octane.environments_manager', icon='WORLD')
        layout.operator('octane.transform_hdri', icon='FILE_3D')
        layout.separator()
        layout.operator('octane.lights_manager', icon='OUTLINER_OB_LIGHT')
        layout.operator('octane.set_light', icon='LIGHT')
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
        layout.operator('octane.cameras_manager', icon='VIEW_CAMERA')
        layout.separator()
        layout.operator('octane.change_obj_props', icon='PROPERTIES')
        layout.operator('octane.change_renderid', icon='FILE_IMAGE')
        layout.separator()
        layout.operator('octane.open_compositor', icon='NODE_COMPOSITING')

class OctaneInfoMenu(Menu):
    bl_label = 'Info'
    bl_idname = 'OCTANE_MT_info'

    def draw(self, context):
        layout = self.layout

        layout.label(text='Otoy')
        layout.operator('wm.url_open', icon='URL', text='Documents').url = 'https://docs.otoy.com'
        layout.operator('wm.url_open', icon='URL', text='Forum').url = 'https://render.otoy.com/forum/index.php'
        layout.operator('wm.url_open', icon='URL', text='General').url = 'https://render.otoy.com/forum/viewforum.php?f=9'
        layout.operator('wm.url_open', icon='URL', text='Blender').url = 'https://render.otoy.com/forum/viewforum.php?f=32'
        layout.separator()

        layout.label(text='Connect')
        layout.operator('wm.url_open', icon='URL', text='Releases').url = 'https://render.otoy.com/forum/viewforum.php?f=113'
        layout.operator('wm.url_open', icon='URL', text='Bug Reports').url = 'https://render.otoy.com/forum/viewforum.php?f=114'
        layout.operator('wm.url_open', icon='URL', text='User Requests').url = 'https://render.otoy.com/forum/viewforum.php?f=115'
        layout.operator('wm.url_open', icon='URL', text='Facebook Group').url = 'https://www.facebook.com/groups/500738480259364'
        layout.separator()

        layout.label(text='Resources')
        layout.operator('wm.url_open', icon='URL', text='ArtStation').url = 'https://www.artstation.com/'
        layout.operator('wm.url_open', icon='URL', text='Pinterest').url = 'https://www.pinterest.com/'
        layout.operator('wm.url_open', icon='URL', text='Behance').url = 'https://www.behance.net/'
        layout.operator('wm.url_open', icon='URL', text='HDRIHaven').url = 'https://hdrihaven.com/hdris/'
        layout.operator('wm.url_open', icon='URL', text='CC0 Textures').url = 'https://cc0textures.com/'
        layout.separator()

        layout.label(text='Plugin')
        layout.operator('wm.url_open', icon='URL', text='Wiki').url = 'https://github.com/Yichen-Dou/OC-Blender-Helper-Addon'
        layout.operator('wm.url_open', icon='URL', text='Downloads').url = 'https://github.com/Yichen-Dou/OC-Blender-Helper-Addon/releases'
        layout.separator()
        
        layout.label(text='Ver.{}.{}.{}'.format(bl_info['version'][0], bl_info['version'][1], bl_info['version'][2]))

class OctaneLightListItem(PropertyGroup):
    obj: PointerProperty(
        name="Object",
        type=bpy.types.Object
    )
    tag: StringProperty(
        name="Tag", 
        default="Unknown"
    )
    icon: StringProperty(
        name="Icon", 
        default="Unknown"
    )

class OctaneWorldListItem(PropertyGroup):
    node: StringProperty(
        name="Node"
    )

class OCTANE_UL_light_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item.obj, 'name', text='', emboss=False, icon=item.icon)
        elif self.layout_type in {'GRID'}: 
            layout.alignment = 'CENTER' 
            layout.label(text="", icon=item.icon)

class OCTANE_UL_world_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ntree = context.scene.world.node_tree
        index = context.scene.oc_worlds_index

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            ''' Due to restrictions of Blender. Cannot rename node for now
            if(item.node not in ntree.nodes):
                layout.prop(ntree.get_output_node('octane'), 'name', emboss=False, icon='NODE', text='')
                refresh_worlds_list(context)
            else:
                layout.prop(ntree.nodes[item.node], 'name', emboss=False, icon='NODE', text='')
            '''
            if(ntree.nodes[item.node].is_active_output):
                layout.label(text=item.node, icon='NODE_SEL')
            else:
                layout.label(text=item.node, icon='NODE')
        elif self.layout_type in {'GRID'}: 
            layout.alignment = 'CENTER' 
            layout.label(text="", icon='NODE')

# Register and Unregister
classes = (
    VIEW3D_MT_object_octane,
    VIEW3D_MT_edit_mesh_octane,
    OctaneMaterialsMenu,
    OctaneEnvironmentMenu,
    OctaneRenderMenu,
    OctaneInfoMenu,
    OctaneLightListItem,
    OCTANE_UL_light_list,
    OctaneWorldListItem,
    OCTANE_UL_world_list
)

def object_menu_func(self, context):
    if context.scene.render.engine == 'octane':
        self.layout.menu('VIEW3D_MT_object_octane', icon_value=get_icon('OCT_RENDER'))
        self.layout.separator()

def edit_menu_func(self, context):
    if context.scene.render.engine == 'octane':
        self.layout.menu('VIEW3D_MT_edit_mesh_octane', icon_value=get_icon('OCT_RENDER'))
        self.layout.separator()

def selected_mat_get(self):
    context = bpy.context
    if(context.active_object):
        if(context.active_object.active_material):
            return bpy.context.active_object.active_material.name
    return ''

def selected_mat_set(self, value):
    if(value!=''):
        assign_material(bpy.context, bpy.data.materials[value])

def register():
    register_icons()
    register_operators()
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Material.copied_mat = None
    bpy.types.Scene.selected_mat = StringProperty(default='', get=selected_mat_get, set=selected_mat_set)
    bpy.types.Scene.is_smooth = BoolProperty(name='Always smooth materials', default=True)
    bpy.types.Scene.oc_lights = CollectionProperty(type=OctaneLightListItem)
    bpy.types.Scene.oc_lights_index = IntProperty(name='Light', default=0)
    bpy.types.Scene.oc_worlds = CollectionProperty(type=OctaneWorldListItem)
    bpy.types.Scene.oc_worlds_index = IntProperty(name='World', default=0)
    bpy.types.VIEW3D_MT_object_context_menu.prepend(object_menu_func)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.prepend(edit_menu_func)

def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(edit_menu_func)
    bpy.types.VIEW3D_MT_object_context_menu.remove(object_menu_func)
    del bpy.types.Scene.oc_lights_index
    del bpy.types.Scene.oc_lights
    del bpy.types.Scene.is_smooth
    del bpy.types.Scene.selected_mat
    del bpy.types.Material.copied_mat
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    unregister_operators()
    unregister_icons()

if __name__ == "__main__":
    register()