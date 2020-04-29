import bpy
from bpy.props import StringProperty, CollectionProperty, PointerProperty
from bpy.types import PropertyGroup, UIList

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

class OCTANE_UL_light_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item.obj, 'name', text='', emboss=False, icon=item.icon)
        elif self.layout_type in {'GRID'}: 
            layout.alignment = 'CENTER' 
            layout.label(text="", icon=item.icon)