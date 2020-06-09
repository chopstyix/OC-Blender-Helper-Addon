import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty

def remove_link(ntree, node, input):
    if(node.inputs[input].is_linked):
        ntree.links.remove(node.inputs[input].links[0])

class OctaneConnectTransformProjection(Operator):
    bl_label = 'Transform and Projection'
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
        if(context.object and context.object.type == 'MESH'):
            mat = context.object.active_material
            ntree = mat.node_tree
            active_node = ntree.nodes.active
            if('Projection' in active_node.inputs and 'Transform' in active_node.inputs):
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
        active_node = ntree.nodes.active

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