import bpy

supported_textures = [
    'opacity',
    'ao',
    'albedo',
    'specular',
    'roughness',
    'metalness',
    'displacement',
    'translucency',
    'normal',
    'bump',
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

def add_components_tex(ntree, components):
    prefs = bpy.context.preferences.addons['Octane_Helper'].preferences
    y_exp = 620

    transNode = ntree.nodes.new('ShaderNodeOct3DTransform')
    transNode.name = 'transform'
    transNode.location = (-1200, 300)

    for component in components:
        texNode = ntree.nodes.new('ShaderNodeOctImageTex')
        texNode.location = (-720, y_exp)
        texNode.image = bpy.data.images.load(component['path'])
        texNode.show_texture = True
        texNode.name = component['type']
        if(component['type'] == 'displacement' and prefs.disp_type == "VERTEX"):
            texNode.border_mode = 'OCT_BORDER_MODE_CLAMP'
        ntree.links.new(ntree.nodes['transform'].outputs[0], texNode.inputs['Transform'])
        y_exp += -320

def group_into_empty(objs):
    bpy.ops.object.empty_add(type='SPHERE', radius=0.2)
    empty = bpy.context.view_layer.objects.active
    for obj in objs:
        obj.parent = empty
