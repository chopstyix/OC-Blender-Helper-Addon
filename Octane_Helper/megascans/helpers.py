import bpy
import socket
from .. operators.nodes import get_y_nodes

supported_textures = [
    'translucency',
    # 'ao', # Disabled cause of my dislike for 'ao' -- # OPSTYIX Patch
    'albedo',
    'specular',
    'roughness',
    'metalness',
    'opacity',    
    'bump',
    'normal',
    'displacement',
    'fuzz',
    'cavity',
    'curvature'
]

# Helper functions
def display_view3d():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                override = {'window': window, 'screen': screen, 'area': area}
                return override
    return {}

def component_sort(component):
    return supported_textures.index(component['type'])

def get_component(components, name):
    return [component for component in components if component['type'] == name][0]

def add_components_tex(ntree, element):
    prefs = bpy.context.preferences.addons['Octane_Helper'].preferences
    components = element['components']
    y_exp = 620

    transform_node = ntree.nodes.new('Octane3DTransformation')
    transform_node.name = 'transform'

    use_projection = (('surface' in element['categories'] or 'surface' in element['tags']) and prefs.use_projection_surface)
    if(use_projection):
        projection_node = ntree.nodes.new(prefs.surface_projection)
        projection_node.name = 'projection'
    
    texNodes = []

    for component in components:
        if component['type'] in ['albedo','diffuse','translucency','normal']:
            texNode = ntree.nodes.new('OctaneRGBImage')
        else:
            texNode = ntree.nodes.new('OctaneGreyscaleImage')
        texNode.location = (-720, y_exp)
        texNode.image = bpy.data.images.load(component['path'])
        texNode.show_texture = True
        texNode.name = component['type']
        texNode.label = component['type']
        if(component['type'] == 'displacement' and prefs.disp_type == "VERTEX"):
            texNode.border_mode = 'OCT_BORDER_MODE_CLAMP'
        ntree.links.new(ntree.nodes['transform'].outputs[0], texNode.inputs['UV transform'])
        if(use_projection):
            ntree.links.new(ntree.nodes['projection'].outputs[0], texNode.inputs['UV transform'])
        texNodes.append(texNode)
        y_exp += -320
    
    transform_node.location = (-1200, get_y_nodes(ntree, texNodes, 'Mid'))
    if(use_projection):
        projection_node.location = (-1200, transform_node.location.y - 350)

def group_into_empty(objs, name):
    bpy.ops.object.empty_add(type='SPHERE', radius=0.2)
    empty = bpy.context.view_layer.objects.active
    empty.name = name
    for obj in objs:
        obj.parent = empty

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                return True
        s.close()
        return False

def is_official_here():
    if('load_plugin' in [handler.__name__.lower() for handler in bpy.app.handlers.load_post]):
        return True
    return False

def is_me_here():
    if('load_ms_module' in [handler.__name__.lower() for handler in bpy.app.handlers.load_post]):
        return True
    return False

def is_in_element(items, element):
    for item in items:
        if item in element['categories'] or item in element['tags']:
            return True
    return False

def notify(msg, title, icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=msg)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
