import bpy
import addon_utils
from bpy.types import Menu

class VIEW3D_MT_object_octane(Menu):
    bl_label = 'Octane'

    def draw(self, context):
        layout = self.layout
        layout.menu(OctaneMaterialsMenu.bl_idname, icon='MATSPHERE')
        layout.menu(OctaneEnvironmentMenu.bl_idname, icon='MAT_SPHERE_SKY')
        layout.menu(OctaneRenderMenu.bl_idname, icon='RESTRICT_RENDER_OFF')
        layout.menu(OctaneInfoMenu.bl_idname, icon='QUESTION')

class VIEW3D_MT_edit_mesh_octane(Menu):
    bl_label = 'Octane'

    def draw(self, context):
        layout = self.layout
        layout.menu(OctaneMaterialsMenu.bl_idname)

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
        layout.operator('octane.assign_emission', icon='LIGHT', text='RGB Emission Material').emission_type = 'RGB'
        layout.operator('octane.assign_emission', icon='LIGHT', text='Texture Emission Material').emission_type = 'TEX'
        layout.operator('octane.assign_emission', icon='LIGHT', text='IES Emission Material').emission_type = 'IES'
        layout.operator('octane.assign_colorgrid', icon='LIGHTPROBE_GRID')
        layout.operator('octane.assign_uvgrid', icon='MESH_GRID')
        layout.operator('octane.assign_sss', icon='SPHERECURVE')
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
        layout.operator('octane.update_display', icon='LONGDISPLAY')
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
        layout.operator('octane.cameras_manager', icon='VIEW_CAMERA')
        layout.separator()
        layout.operator('octane.manage_imager', icon='IMAGE')
        layout.operator('octane.manage_postprocess', icon='CAMERA_STEREO')
        layout.operator('octane.manage_denoiser', icon='OUTLINER_OB_LIGHTPROBE')
        layout.operator('octane.manage_render_passes', icon='IMAGE_REFERENCE')
        layout.operator('octane.manage_render_layers', icon='RENDERLAYERS')
        layout.operator('octane.toggle_claymode', icon='SCULPTMODE_HLT')
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
        
        version = [addon.bl_info['version'] for addon in addon_utils.modules() if (addon.bl_info['name'] == 'Octane Helper')][0]
        layout.label(text='Ver.{}.{}.{}'.format(version[0], version[1], version[2]))