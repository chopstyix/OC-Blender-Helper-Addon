import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty

def update_backplate(self, context):
    world = context.scene.world
    ntree = world.node_tree
    outNode = ntree.get_output_node('octane')
    texenvNode = outNode.inputs['Octane VisibleEnvironment'].links[0].from_node
    texenvNode.inputs['Texture'].default_value = self.backplate_color

# Classes
class OctaneAddBackplate(Operator):
    bl_label = 'Add Backplate'
    bl_idname = 'octane.add_backplate'
    bl_options = {'REGISTER', 'UNDO'}

    backplate_color: FloatVectorProperty(
        name="Color",
        size=4,
        default = (1, 1, 1, 1),
        min = 0,
        max = 1,
        subtype="COLOR")
    
    @classmethod
    def poll(cls, context):
        if(context.scene.world.use_nodes):
            world = context.scene.world
            ntree = world.node_tree
            outNode = ntree.get_output_node('octane')
            if(outNode):
                return (not outNode.inputs['Octane VisibleEnvironment'].is_linked)
            else:
                return False
        else:
            return False
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'backplate_color')
    
    def execute(self, context):
        world = context.scene.world
        ntree = world.node_tree
        outNode = ntree.get_output_node('octane')
        texenvNode = ntree.nodes.new('ShaderNodeOctTextureEnvironment')
        texenvNode.location = (outNode.location.x, outNode.location.y-200)
        texenvNode.inputs['Texture'].default_value = self.backplate_color
        texenvNode.inputs['Visable env Backplate'].default_value = True
        outNode = ntree.get_output_node('octane')
        ntree.links.new(texenvNode.outputs[0], outNode.inputs['Octane VisibleEnvironment'])
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneRemoveBackplate(Operator):
    bl_label = 'Remove Backplate'
    bl_idname = 'octane.remove_backplate'
    bl_options = {'REGISTER', 'UNDO'}
   
    @classmethod
    def poll(cls, context):
        if(context.scene.world.use_nodes):
            world = context.scene.world
            ntree = world.node_tree
            outNode = ntree.get_output_node('octane')
            if(outNode):
                return (outNode.inputs['Octane VisibleEnvironment'].is_linked)
            else:
                return False
        else:
            return False
    
    def execute(self, context):
        world = context.scene.world
        ntree = world.node_tree
        outNode = ntree.get_output_node('octane')
        link = outNode.inputs['Octane VisibleEnvironment'].links[0]
        ntree.nodes.remove(link.from_node)
        ntree.nodes.update()
        return {'FINISHED'}

class OctaneModifyBackplate(Operator):
    bl_label = 'Modify Backplate'
    bl_idname = 'octane.modify_backplate'
    bl_options = {'REGISTER', 'UNDO'}
   
    backplate_color: FloatVectorProperty(
        name="Color",
        size=4,
        default = (1, 1, 1, 1),
        min = 0,
        max = 1,
        subtype="COLOR",
        update=update_backplate)
    
    @classmethod
    def poll(cls, context):
        if(context.scene.world.use_nodes):
            world = context.scene.world
            ntree = world.node_tree
            outNode = ntree.get_output_node('octane')
            if(outNode):
                if (outNode.inputs['Octane VisibleEnvironment'].is_linked):
                    texenvNode = outNode.inputs['Octane VisibleEnvironment'].links[0].from_node
                    if (texenvNode.bl_idname == 'ShaderNodeOctTextureEnvironment'):
                        return not texenvNode.inputs['Texture'].is_linked
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'backplate_color')
    
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        world = context.scene.world
        ntree = world.node_tree
        outNode = ntree.get_output_node('octane')
        texenvNode = outNode.inputs['Octane VisibleEnvironment'].links[0].from_node
        self.backplate_color = texenvNode.inputs['Texture'].default_value
        wm = context.window_manager
        return wm.invoke_props_dialog(self)