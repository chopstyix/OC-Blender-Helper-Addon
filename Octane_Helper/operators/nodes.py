import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty, StringProperty

def remove_link(ntree, node, input=None, side=0):
    if(side == 0):
        if(node.inputs[input].is_linked):
            ntree.links.remove(node.inputs[input].links[0])
    else:
        if(node.outputs[0].is_linked):
            ntree.links.remove(node.outputs[0].links[0])

def remove_connected_nodes(ntree, node):
    for input in node.inputs:
        for link in input.links:
            remove_connected_nodes(ntree, link.from_node)
            ntree.nodes.remove(link.from_node)

def get_connected_nodes(node):
    result = []
    for input in node.inputs:
        for link in input.links:
            result.append(link.from_node)
            result += get_connected_nodes(link.from_node)
    return result

def get_y(ntree, target, type):
    if(not ntree.get_output_node('octane')):
        return 0
    ys = [node.location.y for node in ntree.nodes if node.bl_idname == target]
    if(type == 'Min'):
        return min(ys)
    elif(type == 'Max'):
        return max(ys)
    elif(type == 'Mid'):
        return (min(ys)+max(ys))/2
    else:
        return 0

def get_y_nodes(ntree, nodes, type):
    if(not ntree.get_output_node('octane')):
        return 0
    ys = [node.location.y for node in nodes]
    if(type == 'Min'):
        return min(ys)
    elif(type == 'Max'):
        return max(ys)
    elif(type == 'Mid'):
        return (min(ys)+max(ys))/2
    else:
        return 0

class OctaneConnectTransformProjection(Operator):
    bl_label = 'Add Transform and Projection'
    bl_idname = 'octane.connect_transform_projection'
    bl_options = {'REGISTER', 'UNDO'}

    use_transform: BoolProperty(default=True, name='Enable Transform')

    use_projection: BoolProperty(default=False, name='Enable Projection')

    transform_type: EnumProperty(
        items = [
            ('OctaneScale', 'Scale Transform', ''),
            ('OctaneRotation', 'Rotate Transform', ''),
            ('OctaneTransformValue', 'Full Transform', ''),
            ('Octane2DTransformation', '2D Transform', ''),
            ('Octane3DTransformation', '3D Transform', '')
        ],
        default = 'OctaneTransformValue'
    )

    projection_type: EnumProperty(
        items = [
            ('OctaneBox', 'Box Projection', ''),
            ('OctaneCylindrical', 'Cylindrical Projection', ''),
            ('OctanePerspective', 'Perspective Projection', ''),
            ('OctaneSpherical', 'Spherical Projection', ''),
            ('OctaneMeshUVProjection', 'UVW Projection', ''),
            ('OctaneXYZToUVW', 'XYZ Projection', ''),
            ('OctaneTriplanar', 'Triplanar Projection', ''),
            ('OctaneOSLDelayedUV', 'OSL Delayed Projection', ''),
            ('OctaneOSLProjection', 'OSL Projection', '')
        ],
        default = 'OctaneMeshUVProjection'
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
        if(context.object.type == 'MESH'):
            mat = context.object.active_material
            ntree = mat.node_tree
        elif(context.object.type == 'LIGHT'):
            ntree = context.object.data.node_tree
        else:
            self.report({'ERROR'}, 'Not supported')
            return {'CANCELLED'}

        active_nodes = context.selected_nodes

        if(self.use_transform):
            transform_node = ntree.nodes.new(self.transform_type)
            transform_node.location = (active_nodes[0].location.x - 320, get_y_nodes(ntree, active_nodes, 'Mid'))

        if(self.use_projection):
            project_node = ntree.nodes.new(self.projection_type)
            if(self.use_transform):
                project_node.location = (transform_node.location.x, transform_node.location.y - 350)
            else:
                project_node.location = (active_nodes[0].location.x - 320, get_y_nodes(ntree, active_nodes, 'Mid'))

        for active_node in active_nodes:
            if(self.use_transform):
                remove_link(ntree, active_node, 'Transform')
                ntree.links.new(active_node.inputs['Transform'], transform_node.outputs[0])

            if(self.use_projection):
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
            if(context.selected_nodes[0].bl_idname in ['OctaneMixMaterial', 'OctaneMixTexture', 'OctaneCosineMixTexture']):
                return True
        return False

    def execute(self, context):
        if(context.object.type == 'MESH'):
            mat = context.object.active_material
            ntree = mat.node_tree
        elif(context.object.type == 'LIGHT'):
            ntree = context.object.data.node_tree
        else:
            self.report({'ERROR'}, 'Not supported')
            return {'CANCELLED'}
        a = None
        b = None

        if(context.selected_nodes[0].bl_idname == 'OctaneMixMaterial'):
            if(context.selected_nodes[0].inputs[1].is_linked):
                a = context.selected_nodes[0].inputs[1].links[0].from_node
                remove_link(ntree, context.selected_nodes[0], 'First material')
            if(context.selected_nodes[0].inputs[2].is_linked):
                b = context.selected_nodes[0].inputs[2].links[0].from_node
                remove_link(ntree, context.selected_nodes[0], 'Second material')
            if(a):
                ntree.links.new(a.outputs[0], context.selected_nodes[0].inputs[2])
            if(b):
                ntree.links.new(b.outputs[0], context.selected_nodes[0].inputs[1])
        else:
            if(context.selected_nodes[0].inputs[1].is_linked):
                a = context.selected_nodes[0].inputs[1].links[0].from_node
                remove_link(ntree, context.selected_nodes[0], 'First texture')
            if(context.selected_nodes[0].inputs[2].is_linked):
                b = context.selected_nodes[0].inputs[2].links[0].from_node
                remove_link(ntree, context.selected_nodes[0], 'Second texture')
            if(a):
                ntree.links.new(a.outputs[0], context.selected_nodes[0].inputs[2])
            if(b):
                ntree.links.new(b.outputs[0], context.selected_nodes[0].inputs[1])

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
        if(context.object.type == 'MESH'):
            mat = context.object.active_material
            ntree = mat.node_tree
        elif(context.object.type == 'LIGHT'):
            ntree = context.object.data.node_tree
        else:
            self.report({'ERROR'}, 'Not supported')
            return {'CANCELLED'}
        remove_connected_nodes(ntree, context.selected_nodes[0])
        return {'FINISHED'}

class OctaneMixBy(Operator):
    bl_label = 'Mix'
    bl_idname = 'octane.mix_by'
    bl_options = {'REGISTER', 'UNDO'}

    mix_type: StringProperty(default='None')

    @classmethod
    def poll(cls, context):
        return len(context.selected_nodes) == 2

    def execute(self, context):
        if(context.object.type == 'MESH'):
            mat = context.object.active_material
            ntree = mat.node_tree
        elif(context.object.type == 'LIGHT'):
            ntree = context.object.data.node_tree
        else:
            self.report({'ERROR'}, 'Not supported')
            return {'CANCELLED'}
        active_nodes = context.selected_nodes
        loc = active_nodes[0].location.copy()

        for active_node in active_nodes:
            remove_link(ntree, active_node, side=1)
            active_node.location.x -= 250
            for node in get_connected_nodes(active_node):
                node.location.x -= 250

        if(len([active_node for active_node in active_nodes if 'Mat' in active_node.bl_idname])):
            mixNode = ntree.nodes.new('OctaneMixMaterial')
            mixNode.location = loc
            ntree.links.new(active_nodes[0].outputs[0], mixNode.inputs[1])
            ntree.links.new(active_nodes[1].outputs[0], mixNode.inputs[2])
        else:
            mixNode = ntree.nodes.new('OctaneMixTexture')
            mixNode.location = loc
            ntree.links.new(active_nodes[0].outputs[0], mixNode.inputs[1])
            ntree.links.new(active_nodes[1].outputs[0], mixNode.inputs[2])

        if(self.mix_type!='None'):
            mixAmountNode = ntree.nodes.new(self.mix_type)
            mixAmountNode.location = (loc.x, loc.y + 300)
            ntree.links.new(mixAmountNode.outputs[0], mixNode.inputs['Amount'])

        ntree.nodes.update()
        return {'FINISHED'}

class OctaneNodeConvertTo(Operator):
    bl_label = 'Convert Node To'
    bl_idname = 'octane.node_convert_to'
    bl_options = {'REGISTER', 'UNDO'}

    node_target: StringProperty(default='None')

    @classmethod
    def poll(cls, context):
        if(not len(context.selected_nodes)):
            return False
        if('Projection' in context.selected_nodes[0].bl_idname):
            return True
        elif('Transform' in context.selected_nodes[0].bl_idname):
            return True
        elif('Mat' in context.selected_nodes[0].bl_idname):
            return True
        return False

    def execute(self, context):
        if(self.node_target!='None'):
            except_list = ['Transmission']
            if(context.object.type == 'MESH'):
                mat = context.object.active_material
                ntree = mat.node_tree
            elif(context.object.type == 'LIGHT'):
                ntree = context.object.data.node_tree
            else:
                self.report({'ERROR'}, 'Not supported')
                return {'CANCELLED'}
            if('Projection' in context.selected_nodes[0].bl_idname and 'Projection' in self.node_target):
                pass
            elif('Transform' in context.selected_nodes[0].bl_idname and 'Transform' in self.node_target):
                pass
            elif('Mat' in context.selected_nodes[0].bl_idname and 'Mat' in self.node_target):
                pass
            else:
                self.report({'ERROR'}, 'Not supported')
                return {'CANCELLED'}
            active_node = context.selected_nodes[0]
            newNode = ntree.nodes.new(self.node_target)
            newNode.location = active_node.location

            # A list of socket objects, not strs
            # Different names for Diffuse color in Universal and Other shaders. We need to handle it. This shoule be removed in the future
            common_sockets = [in_socket for in_socket in active_node.inputs if (in_socket.name in newNode.inputs) or (in_socket.name in ['Albedo', 'Diffuse'] and ('Albedo' in newNode.inputs or 'Diffuse' in newNode.inputs))]
            for common_socket in common_sockets:
                if(common_socket.is_linked):
                    if(common_socket.name == 'Albedo' and 'Diffuse' in newNode.inputs):
                        ntree.links.new(common_socket.links[0].from_node.outputs[0], newNode.inputs['Diffuse'])
                    elif(common_socket.name == 'Diffuse' and 'Albedo' in newNode.inputs):
                        ntree.links.new(common_socket.links[0].from_node.outputs[0], newNode.inputs['Albedo'])
                    else:
                        ntree.links.new(common_socket.links[0].from_node.outputs[0], newNode.inputs[common_socket.name])
                elif(hasattr(common_socket, 'default_value') and common_socket.name not in except_list):
                    if(common_socket.name == 'Albedo' and 'Diffuse' in newNode.inputs):
                        newNode.inputs['Diffuse'].default_value = common_socket.default_value
                    elif(common_socket.name == 'Diffuse' and 'Albedo' in newNode.inputs):
                        newNode.inputs['Albedo'].default_value = common_socket.default_value
                    else:
                        if(hasattr(newNode.inputs[common_socket.name], 'default_value')):
                            newNode.inputs[common_socket.name].default_value = common_socket.default_value
                        else:
                            rgb_node = ntree.nodes.new('OctaneRGBColor')
                            rgb_node.inputs['Color'].default_value = common_socket.default_value
                            rgb_node.location = (newNode.location.x - 200, newNode.location.y)
                            ntree.links.new(rgb_node.outputs[0], newNode.inputs[common_socket.name])

            # Connect output
            if(active_node.outputs[0].is_linked):
                target_sockets = [link.to_socket for link in active_node.outputs[0].links]
                for target_socket in target_sockets:
                    ntree.links.new(target_socket, newNode.outputs[0])

            ntree.nodes.remove(active_node)
            ntree.nodes.update()
        return {'FINISHED'}
