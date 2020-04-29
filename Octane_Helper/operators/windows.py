import bpy 
from bpy.types import Operator

class OctaneOpenCompositor(Operator):
    bl_label = 'Open Compositor'
    bl_idname = 'octane.open_compositor'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.screen.userpref_show("INVOKE_DEFAULT")
        area = bpy.context.window_manager.windows[-1].screen.areas[0]
        area.ui_type = 'CompositorNodeTree'
        bpy.context.scene.use_nodes = True
        bpy.context.space_data.show_backdrop = True
        return {'FINISHED'}