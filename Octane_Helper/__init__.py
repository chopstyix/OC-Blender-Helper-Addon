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
from bpy.props import EnumProperty
from . megascans import register_megascans, unregister_megascans
from . icons import register_icons, unregister_icons
from . operators import register_operators, unregister_operators
from . menus import register_menus, unregister_menus
import rna_keymap_ui

bl_info = {
    "name": "Octane Helper",
    "description": "A helper addon for Octane Blender edition",
    "author": "Yichen Dou",
    "version": (2, 5, 0),
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

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "brdf_model")
        col = layout.column()
        kc = bpy.context.window_manager.keyconfigs.addon
        for km, kmi in addon_keymaps:
            km = km.active()
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

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