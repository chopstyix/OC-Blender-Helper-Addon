import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import PropertyGroup, UIList

class OctanePresetListItem(PropertyGroup):
    name: StringProperty(
        name='Preset',
        default='Unknown'
    )

class OCTANE_UL_preset_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        index = context.scene.oc_presets

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon='COPY_ID')
        elif self.layout_type in {'GRID'}: 
            layout.alignment = 'CENTER' 
            layout.label(text="", icon='COPY_ID')