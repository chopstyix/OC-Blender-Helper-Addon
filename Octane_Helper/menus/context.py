import bpy
import addon_utils
from bpy.types import Menu
from bpy.props import StringProperty
from .. icons import get_icon

def object_menu_func(self, context):
    if context.scene.render.engine == 'octane':
        self.layout.menu('VIEW3D_MT_object_octane', icon_value=get_icon('OCT_RENDER'))
        self.layout.separator()

def edit_menu_func(self, context):
    if context.scene.render.engine == 'octane':
        self.layout.menu('VIEW3D_MT_edit_mesh_octane', icon_value=get_icon('OCT_RENDER'))
        self.layout.separator()

def node_menu_func(self, context):
    if context.scene.render.engine == 'octane' and context.space_data.shader_type == 'OBJECT':
        self.layout.menu('NODE_MT_node_octane', icon_value=get_icon('OCT_RENDER'))
        self.layout.separator()

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
        layout.menu(OctaneMaterialsMenu.bl_idname, icon='MATSPHERE')
        layout.menu(OctaneRenderMenu.bl_idname, icon='RESTRICT_RENDER_OFF')
        layout.menu(OctaneInfoMenu.bl_idname, icon='QUESTION')

class NODE_MT_node_octane(Menu):
    bl_label = 'Octane'

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.enabled = (len(context.selected_nodes) and (
            'Mat' in context.selected_nodes[0].bl_idname or 
            'Projection' in context.selected_nodes[0].bl_idname or
            'Transform' in context.selected_nodes[0].bl_idname))
        col.menu(OctaneNodeConvertToMenu.bl_idname, icon='SHADERFX')
        
        col = layout.column()
        col.enabled = (len(context.selected_nodes) == 2)
        col.menu(OctaneNodeMixByMenu.bl_idname, icon='MOD_MASK')
        layout.separator()
        
        layout.operator('octane.connect_transform_projection', icon='NODETREE')
        layout.separator()
        
        layout.operator('octane.switch_ab', icon='MODIFIER')
        layout.operator('octane.remove_connected_nodes', icon='MODIFIER')

class OctaneNodeConvertToShadersMenu(Menu):
    bl_label = 'Shaders'
    bl_idname = 'OCTANE_MT_node_convert_to_shaders'

    def draw(self, context):
        layout = self.layout
        layout.operator('octane.node_convert_to', text='Universal Material').node_target = 'OctaneUniversalMaterial'
        layout.operator('octane.node_convert_to', text='Diffuse Material').node_target = 'OctaneDiffuseMaterial'
        layout.operator('octane.node_convert_to', text='Glossy Material').node_target = 'OctaneGlossyMaterial'
        layout.operator('octane.node_convert_to', text='Specular Material').node_target = 'OctaneSpecularMaterial'
        layout.operator('octane.node_convert_to', text='Mix Material').node_target = 'OctaneMixMaterial'
        layout.operator('octane.node_convert_to', text='Portal Material').node_target = 'OctanePortalMaterial'
        layout.operator('octane.node_convert_to', text='ShadowCatcher Material').node_target = 'OctaneShadowCatcherMaterial'
        layout.operator('octane.node_convert_to', text='Toon Material').node_target = 'OctaneToonMaterial'
        layout.operator('octane.node_convert_to', text='Metal Material').node_target = 'OctaneMetallicMaterial'
        layout.operator('octane.node_convert_to', text='Layered Material').node_target = 'OctaneLayeredMaterial'
        layout.operator('octane.node_convert_to', text='Composite Material').node_target = 'OctaneCompositeMaterial'
        layout.operator('octane.node_convert_to', text='Hair Material').node_target = 'OctaneHairMaterial'

class OctaneNodeConvertToProjectionsMenu(Menu):
    bl_label = 'Projections'
    bl_idname = 'OCTANE_MT_node_convert_to_projections'

    def draw(self, context):
        layout = self.layout
        layout.operator('octane.node_convert_to', text='Box Projection').node_target = "OctaneBox"
        layout.operator('octane.node_convert_to', text='Cylindrical Projection').node_target = "OctaneCylindrical"
        layout.operator('octane.node_convert_to', text='Perspective Projection').node_target = "OctanePerspective"
        layout.operator('octane.node_convert_to', text='Spherical Projection').node_target = "OctaneSpherical"
        layout.operator('octane.node_convert_to', text='UVW Projection').node_target = "OctaneMeshUVProjection"
        layout.operator('octane.node_convert_to', text='XYZ Projection').node_target = "OctaneXYZToUVW"
        layout.operator('octane.node_convert_to', text='Triplanar Projection').node_target = "OctaneTriplanar"
        layout.operator('octane.node_convert_to', text='OSL Delayed Projection').node_target = "OctaneOSLDelayedUV"
        layout.operator('octane.node_convert_to', text='OSL Projection').node_target = "OctaneOSLProjection"

class OctaneNodeConvertToTransformsMenu(Menu):
    bl_label = 'Transforms'
    bl_idname = 'OCTANE_MT_node_convert_to_transforms'

    def draw(self, context):
        layout = self.layout
        layout.operator('octane.node_convert_to', text='Scale Transform').node_target = "OctaneScale"
        layout.operator('octane.node_convert_to', text='Rotate Transform').node_target = "OctaneRotation"
        layout.operator('octane.node_convert_to', text='Full Transform').node_target = "OctaneTransformValue"
        layout.operator('octane.node_convert_to', text='2D Transform').node_target = "Octane2DTransformation"
        layout.operator('octane.node_convert_to', text='3D Transform').node_target = "Octane3DTransformation"

class OctaneNodeConvertToMenu(Menu):
    bl_label = 'Convert To'
    bl_idname = 'OCTANE_MT_node_convert_to'

    def draw(self, context):
        layout = self.layout
        layout.menu(OctaneNodeConvertToShadersMenu.bl_idname, icon='NODE_MATERIAL')
        layout.menu(OctaneNodeConvertToTransformsMenu.bl_idname, icon='FILE_3D')
        layout.menu(OctaneNodeConvertToProjectionsMenu.bl_idname, icon='AXIS_SIDE')

class OctaneNodeMixByMenu(Menu):
    bl_label = 'Mix By'
    bl_idname = 'OCTANE_MT_node_mix_by'

    def draw(self, context):
        layout = self.layout
        layout.operator('octane.mix_by', text='None').mix_type = 'None'
        layout.operator('octane.mix_by', text='Image Tex').mix_type = 'ShaderNodeOctImageTex'
        layout.operator('octane.mix_by', text='Image Tile Tex').mix_type = 'ShaderNodeOctImageTileTex'
        layout.operator('octane.mix_by', text='Alpha Image Tex').mix_type = 'ShaderNodeOctAlphaImageTex'
        layout.operator('octane.mix_by', text='Float Image Tex').mix_type = 'ShaderNodeOctFloatImageTex'

class OctaneMaterialsMenu(Menu):
    bl_label = 'Materials'
    bl_idname = 'OCTANE_MT_materials'

    def draw(self, context):
        layout = self.layout
        layout.prop_search(context.scene, property='selected_mat', search_data=bpy.data, search_property='materials', text='', icon='MATERIAL')
        layout.separator()
        layout.menu(OctaneBasicMaterialsMenu.bl_idname, icon='NODE_MATERIAL')
        layout.separator()
        layout.operator('octane.assign_emission', icon='LIGHT', text='RGB Emission Material').emission_type = 'RGB'
        layout.operator('octane.assign_emission', icon='LIGHT', text='Texture Emission Material').emission_type = 'TEX'
        layout.operator('octane.assign_emission', icon='LIGHT', text='IES Emission Material').emission_type = 'IES'
        layout.separator()
        layout.operator('octane.assign_clear_glass', icon='FCURVE')
        layout.operator('octane.assign_sss', icon='SPHERECURVE')
        layout.separator()
        layout.operator('octane.assign_pattern', icon='TEXTURE', text='Pattern Material')
        layout.operator('octane.assign_colorgrid', icon='LIGHTPROBE_GRID')
        layout.operator('octane.assign_uvgrid', icon='LIGHTPROBE_GRID')
        layout.separator()
        layout.operator('octane.assign_mantaflow_volume', icon='PHYSICS')
        layout.operator('octane.assign_embergen_volume', icon='PHYSICS')
        layout.separator()
        layout.operator('octane.convert_mat', icon='EXPERIMENTAL')
        layout.operator('octane.open_shader_editor', icon='NODETREE')
        layout.separator()
        layout.operator('octane.rename_mat', icon='GREASEPENCIL')
        layout.operator('octane.copy_mat', icon='COPYDOWN')
        layout.operator("octane.duplicate_mat", icon='DUPLICATE')
        layout.operator('octane.paste_mat', icon='PASTEDOWN')
        if(bpy.types.Material.copied_mat!=None):
            layout.label(text='['+((bpy.types.Material.copied_mat.name[:16] + '..') if len(bpy.types.Material.copied_mat.name) > 16 else bpy.types.Material.copied_mat.name)+']')
        layout.separator()
        layout.prop(context.scene, 'is_smooth')
        layout.operator('octane.autosmooth', icon='SMOOTHCURVE')

class OctaneBasicMaterialsMenu(Menu):
    bl_label = 'Shaders'
    bl_idname = 'OCTANE_MT_basic_materials'
    
    def draw(self, context):
        layout = self.layout
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
        layout.operator('octane.select_lights', icon='LIGHT')
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
        layout.operator('wm.url_open', icon='URL', text='Wiki').url = 'https://github.com/llennoco22/OC-Blender-Helper-Addon'
        layout.operator('wm.url_open', icon='URL', text='Downloads').url = 'https://github.com/llennoco22/OC-Blender-Helper-Addon/releases'
        layout.separator()
        
        version = [addon.bl_info['version'] for addon in addon_utils.modules() if (addon.bl_info['name'] == 'Octane Helper')][0]
        layout.label(text='Ver.{}.{}.{}'.format(version[0], version[1], version[2]))
