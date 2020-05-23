import bpy
from bpy.props import StringProperty, CollectionProperty, PointerProperty, BoolProperty
from bpy.types import PropertyGroup, UIList

def get_bool_light_on(self):
    if(self.obj.type == 'LIGHT'):
        # Search node in the active light object for emissive node
        for node in self.obj.data.node_tree.nodes:
            if(node.bl_idname=='ShaderNodeOctDiffuseMat' and node.inputs['Emission'].is_linked):
                return node.inputs['Opacity'].default_value != 0.0
            elif(node.bl_idname=='ShaderNodeOctToonDirectionLight' or node.bl_idname=='ShaderNodeOctToonPointLight'):
                return node.inputs['Power'].default_value != 0.0
    elif(self.obj.type == 'MESH'):
        if(self.obj.active_material):
            for node in self.obj.active_material.node_tree.nodes:
                if(node.bl_idname=='ShaderNodeOctDiffuseMat' and node.inputs['Emission'].is_linked):
                    return node.inputs['Opacity'].default_value != 0.0
                elif(node.bl_idname=='ShaderNodeOctToonDirectionLight' or node.bl_idname=='ShaderNodeOctToonPointLight'):
                    return node.inputs['Power'].default_value != 0.0
    return False

def set_bool_light_on(self, value):
    if(self.obj.type == 'LIGHT'):
        # Search node in the active light object for emissive node
        for node in self.obj.data.node_tree.nodes:
            if(node.bl_idname=='ShaderNodeOctDiffuseMat' and node.inputs['Emission'].is_linked):
                node.inputs['Opacity'].default_value = 1.0 if value else 0.0
            elif(node.bl_idname=='ShaderNodeOctToonDirectionLight' or node.bl_idname=='ShaderNodeOctToonPointLight'):
                node.inputs['Power'].default_value = 1.0 if value else 0.0
    elif(self.obj.type == 'MESH'):
        if(self.obj.active_material):
            for node in self.obj.active_material.node_tree.nodes:
                if(node.bl_idname=='ShaderNodeOctDiffuseMat' and node.inputs['Emission'].is_linked):
                    node.inputs['Opacity'].default_value = 1.0 if value else 0.0
                elif(node.bl_idname=='ShaderNodeOctToonDirectionLight' or node.bl_idname=='ShaderNodeOctToonPointLight'):
                    node.inputs['Power'].default_value = 1.0 if value else 0.0    

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
    is_on: BoolProperty(default=True, get=get_bool_light_on, set=set_bool_light_on)

class OCTANE_UL_light_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, 'is_on', icon=item.icon, icon_only=True, toggle=True)
            row.prop(item.obj, 'name', text='', emboss=False)
        elif self.layout_type in {'GRID'}: 
            layout.alignment = 'CENTER' 
            layout.label(text="", icon=item.icon)