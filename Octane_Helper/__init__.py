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
from bpy.types import AddonPreferences
from bpy.props import EnumProperty, IntProperty, BoolProperty
from . megascans import register_megascans, unregister_megascans
from . icons import register_icons, unregister_icons
from . operators import register_operators, unregister_operators
from . menus import register_menus, unregister_menus
import rna_keymap_ui

bl_info = {
    "name": "Octane Helper",
    "description": "A helper addon for Octane Blender edition",
    "author": "Yichen Dou",
    "version": (2, 7, 0),
    "blender": (2, 81, 0),
    "warning": "",
    "wiki_url": "https://github.com/Yichen-Dou/OC-Blender-Helper-Addon",
    "support": "COMMUNITY",
    "category": "3D View"
}

addon_keymaps = []

# Prefs for the addon
class OctaneHelperPrefs(AddonPreferences):
    bl_idname = __name__

    brdf_model: EnumProperty(
        name='BRDF Model',
        items=[
            ('OCTANE_BRDF_OCTANE', 'Octane', ''),
            ('OCTANE_BRDF_BECKMANN', 'Beckmann', ''),
            ('OCTANE_BRDF_GGX', 'GGX', ''),
            ('OCTANE_BRDF_WARD', 'Ward', '')
        ],
        default='OCTANE_BRDF_OCTANE'
    )

    disp_type: EnumProperty(
        items=[
            ('TEXTURE', 'Texture', 'Octane Texture Displacement'),
            ('VERTEX', 'Vertex', 'Octane Vertex Displacement')
        ],
        name="Displacement Mode",
        description="Set default Octane displacement mode",
        default="TEXTURE"
    )

    disp_level_vertex: IntProperty(
        name="Subdivision",
        min=0,
        max=6,
        default=6
    )

    is_cavity_enabled: BoolProperty(
        name="Enable Cavity map",
        default=False
    )

    is_curvature_enabled: BoolProperty(
        name="Enable Curvature map",
        default=False
    )

    is_bump_enabled: BoolProperty(
        name="Enable Bump map",
        default=False
    )

    is_fuze_enabled: BoolProperty(
        name="Enable Fuze map",
        default=False
    )

    use_projection_surface: BoolProperty(
        name='Use Projection for Surface Materials',
        default=False
    )

    surface_projection: EnumProperty(
        items = [
            ('ShaderNodeOctBoxProjection', 'Box Projection', ''),
            ('ShaderNodeOctCylProjection', 'Cylindrical Projection', ''),
            ('ShaderNodeOctPerspProjection', 'Perspective Projection', ''),
            ('ShaderNodeOctSphericalProjection', 'Spherical Projection', ''),
            ('ShaderNodeOctUVWProjection', 'UVW Projection', ''),
            ('ShaderNodeOctXYZProjection', 'XYZ Projection', ''),
            ('ShaderNodeOctTriplanarProjection', 'Triplanar Projection', ''),
            ('ShaderNodeOctOSLUVProjection', 'OSL Delayed Projection', ''),
            ('ShaderNodeOctOSLProjection', 'OSL Projection', '')
        ],
        default = 'ShaderNodeOctUVWProjection'
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Octane')
        box.prop(self, "brdf_model")
        box.separator()

        box = layout.box()
        box.label(text='Megascans')
        col = box.column(align=True)
        col.prop(self, 'use_projection_surface')
        col.prop(self, 'surface_projection', text='')
        col = box.column(align=True)
        col.prop(self, "disp_type")
        if(self.disp_type == "VERTEX"):
            col.prop(self, "disp_level_vertex")
        col = box.column(align=True)
        col.prop(self, "is_cavity_enabled")
        col.prop(self, "is_curvature_enabled")
        col.prop(self, "is_bump_enabled")
        col.prop(self, "is_fuze_enabled")
        box.separator()

        box = layout.box()
        box.label(text='Keymap')
        kc = bpy.context.window_manager.keyconfigs.addon
        for km, kmi in addon_keymaps:
            km = km.active()
            box.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, box, 0)
        box.separator()
        
def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi_cameras = km.keymap_items.new('octane.cameras_manager', type='C', value='PRESS', alt=True, shift=True)
    kmi_lights = km.keymap_items.new('octane.lights_manager', type='D', value='PRESS', alt=True, shift=True)
    kmi_environments = km.keymap_items.new('octane.environments_manager', type='E', value='PRESS', alt=True, shift=True)
    addon_keymaps.append((km, kmi_cameras))
    addon_keymaps.append((km, kmi_lights))
    addon_keymaps.append((km, kmi_environments))

def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

def register():
    bpy.utils.register_class(OctaneHelperPrefs)
    register_keymaps()
    register_icons()
    register_megascans()
    register_operators()
    register_menus()

def unregister():
    unregister_menus()
    unregister_operators()
    unregister_megascans()
    unregister_icons()
    unregister_keymaps()
    bpy.utils.unregister_class(OctaneHelperPrefs)

if __name__ == "__main__":
    register()