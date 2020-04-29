import bpy
from bpy.props import StringProperty, CollectionProperty
from bpy.types import PropertyGroup, UIList

class OctaneWorldListItem(PropertyGroup):
    node: StringProperty(
        name="Node"
    )

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