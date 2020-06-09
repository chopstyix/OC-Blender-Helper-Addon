import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty

def remove_link(ntree, node, input):
    if(node.inputs[input].is_linked):
        ntree.links.remove(node.inputs[input].links[0])

def remove_connected_nodes(ntree, node):
    for input in node.inputs:
        for link in input.links:
            remove_connected_nodes(ntree, link.from_node)
            ntree.nodes.remove(link.from_node)

class OctaneConnectTransformProjection(Operator):
    bl_label = 'Add Transform and Projection'
    bl_idname = 'octane.connect_transform_projection'
    bl_options = {'REGISTER', 'UNDO'}

    use_transform: BoolProperty(default=True, name='Enable Transform')

    use_projection: BoolProperty(default=True, name='Enable Projection')

    transform_type: EnumProperty(
        items = [
            ('ShaderNodeOctScaleTransform', 'Scale Transform', ''),
            ('ShaderNodeOctRotateTransform', 'Rotate Transform', ''),
            ('ShaderNodeOctFullTransform', 'Full Transform', ''),
            ('ShaderNodeOct2DTransform', '2D Transform', ''),
            ('ShaderNodeOct3DTransform', '3D Transform', '')
        ],
        default = 'ShaderNodeOctFullTransform'
    )

    projection_type: EnumProperty(
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

    @classmethod
    def poll(cls, context):
        active_nodes = context.selected_nodes
        if(len(active_nodes) == 0):
            return False
        count = 0
        for active_node in active_nodes:
            if('Projection' in active_node.inputs and 'Transform' in active_node.inputs):
                count += 1
        if(count == len(active_nodes)):
            return True
        return False
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, 'use_transform')
        col.prop(self, 'use_projection')

        col = layout.column(align=True)
        col.enabled = self.use_transform
        col.prop(self, 'transform_type', text='')

        col = layout.column(align=True)
        col.enabled = self.use_projection
        col.prop(self, 'projection_type', text='')

    def execute(self, context):
        mat = context.object.active_material
        ntree = mat.node_tree
        active_nodes = context.selected_nodes

        for active_node in active_nodes:
            if(self.use_transform):
                transform_node = ntree.nodes.new(self.transform_type)
                transform_node.location = (active_node.location.x - 200, active_node.location.y)
                remove_link(ntree, active_node, 'Transform')
                ntree.links.new(active_node.inputs['Transform'], transform_node.outputs[0])
            
            if(self.use_projection):
                project_node = ntree.nodes.new(self.projection_type)
                if(self.use_transform):
                    project_node.location = (transform_node.location.x, transform_node.location.y - 350)
                else:
                    project_node.location = (active_node.location.x - 200, active_node.location.y)
                remove_link(ntree, active_node, 'Projection')
                ntree.links.new(active_node.inputs['Projection'], project_node.outputs[0])

        ntree.nodes.update()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneSwitchAB(Operator):
    bl_label = 'Switch A and B'
    bl_idname = 'octane.switch_ab'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if(len(context.selected_nodes) != 0):
            if(context.selected_nodes[0].bl_idname in ['ShaderNodeOctMixMat', 'ShaderNodeOctMixTex', 'ShaderNodeOctCosineMixTex']):
                return True
        return False

    def execute(self, context):
        ntree = context.object.active_material.node_tree
        a = None
        b = None

        if(context.selected_nodes[0].bl_idname == 'ShaderNodeOctMixMat'):
            if(context.selected_nodes[0].inputs['Material1'].is_linked):
                a = context.selected_nodes[0].inputs['Material1'].links[0].from_node
                remove_link(ntree, context.selected_nodes[0], 'Material1')
            if(context.selected_nodes[0].inputs['Material2'].is_linked):
                b = context.selected_nodes[0].inputs['Material2'].links[0].from_node
                remove_link(ntree, context.selected_nodes[0], 'Material2')
            if(a):
                ntree.links.new(a.outputs[0], context.selected_nodes[0].inputs['Material2'])
            if(b):
                ntree.links.new(b.outputs[0], context.selected_nodes[0].inputs['Material1'])
        else:
            if(context.selected_nodes[0].inputs['Texture1'].is_linked):
                a = context.selected_nodes[0].inputs['Texture1'].links[0].from_node
                remove_link(ntree, context.selected_nodes[0], 'Texture1')
            if(context.selected_nodes[0].inputs['Texture2'].is_linked):
                b = context.selected_nodes[0].inputs['Texture2'].links[0].from_node
                remove_link(ntree, context.selected_nodes[0], 'Texture2')
            if(a):
                ntree.links.new(a.outputs[0], context.selected_nodes[0].inputs['Texture2'])
            if(b):
                ntree.links.new(b.outputs[0], context.selected_nodes[0].inputs['Texture1'])
        
        ntree.nodes.update()
        return {'FINISHED'}

class OctaneRemoveConnectedNodes(Operator):
    bl_label = 'Remove Connected Nodes'
    bl_idname = 'octane.remove_connected_nodes'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if(len(context.selected_nodes) != 0):
            return True
        return False

    def execute(self, context):
        ntree = context.object.active_material.node_tree
        remove_connected_nodes(ntree, context.selected_nodes[0])
        return {'FINISHED'}

