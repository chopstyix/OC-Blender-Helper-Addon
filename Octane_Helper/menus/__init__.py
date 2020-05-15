import bpy
from bpy.props import IntProperty, BoolProperty, CollectionProperty, StringProperty, EnumProperty
from . context import *
from . worlds import *
from . lights import *
from .. icons import get_icon
from .. operators.materials import assign_material, selected_mat_get, selected_mat_set
from .. operators.environments import get_enum_env_presets
from .. operators.objects import get_enum_landscape, update_enum_landscape, get_enum_cloud, update_enum_cloud

def object_menu_func(self, context):
    if context.scene.render.engine == 'octane':
        self.layout.menu('VIEW3D_MT_object_octane', icon_value=get_icon('OCT_RENDER'))
        self.layout.separator()

def edit_menu_func(self, context):
    if context.scene.render.engine == 'octane':
        self.layout.menu('VIEW3D_MT_edit_mesh_octane', icon_value=get_icon('OCT_RENDER'))
        self.layout.separator()

classes = (
    VIEW3D_MT_object_octane,
    VIEW3D_MT_edit_mesh_octane,
    OctaneMaterialsMenu,
    OctaneObjectsMenu,
    OctaneLandscapesMenu,
    OctaneCloudsMenu,
    OctaneEnvironmentMenu,
    OctaneRenderMenu,
    OctaneInfoMenu,
    OctaneLightListItem,
    OCTANE_UL_light_list,
    OctaneWorldListItem,
    OCTANE_UL_world_list
)

def register_menus():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Material.copied_mat = None
    bpy.types.Scene.selected_mat = StringProperty(default='', get=selected_mat_get, set=selected_mat_set)
    bpy.types.Scene.is_smooth = BoolProperty(name='Always smooth materials', default=True)
    bpy.types.Scene.oc_lights = CollectionProperty(type=OctaneLightListItem)
    bpy.types.Scene.oc_lights_index = IntProperty(name='Light', default=0)
    bpy.types.Scene.oc_env_preset = EnumProperty(name='Presets', items=get_enum_env_presets)
    bpy.types.Scene.oc_worlds = CollectionProperty(type=OctaneWorldListItem)
    bpy.types.Scene.oc_worlds_index = IntProperty(name='World', default=0)
    bpy.types.Scene.oc_landscape = EnumProperty(name='landscapes', items=get_enum_landscape, update=update_enum_landscape)
    bpy.types.Scene.oc_cloud = EnumProperty(name='clouds', items=get_enum_cloud, update=update_enum_cloud)
    bpy.types.VIEW3D_MT_object_context_menu.prepend(object_menu_func)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.prepend(edit_menu_func)

def unregister_menus():
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(edit_menu_func)
    bpy.types.VIEW3D_MT_object_context_menu.remove(object_menu_func)
    del bpy.types.Scene.oc_landscape
    del bpy.types.Scene.oc_worlds_index
    del bpy.types.Scene.oc_worlds
    del bpy.types.Scene.oc_lights_index
    del bpy.types.Scene.oc_lights
    del bpy.types.Scene.is_smooth
    del bpy.types.Scene.selected_mat
    del bpy.types.Material.copied_mat
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)