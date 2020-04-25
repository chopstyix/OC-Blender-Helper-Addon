import bpy
from bpy.types import Operator
from bpy.props import EnumProperty

class OctaneManageImager(Operator):
    bl_label = 'Camera Imager'
    bl_idname = 'octane.manage_imager'
    bl_options = {'REGISTER', 'UNDO'}
    
    def draw(self, context):
        oct_cam = context.scene.oct_view_cam
        layout = self.layout
        col = layout.column(align=True)
        col.prop(context.scene.octane, "hdr_tonemap_preview_enable", text="Enable Camera Imager")
        col.prop(context.scene.octane, "use_preview_setting_for_camera_imager")

        col = layout.column(align=True)
        col.enabled = (context.scene.octane.hdr_tonemap_preview_enable and context.scene.octane.use_preview_setting_for_camera_imager)
        col.prop(oct_cam, "camera_imager_order")
        col = layout.column(align=True)
        col.enabled = (context.scene.octane.hdr_tonemap_preview_enable and context.scene.octane.use_preview_setting_for_camera_imager)
        col.prop(oct_cam, "response_type")
        col = layout.column(align=True)
        col.enabled = (context.scene.octane.hdr_tonemap_preview_enable and context.scene.octane.use_preview_setting_for_camera_imager)
        col.prop(oct_cam, "white_balance")
        col = layout.column(align=True)
        col.enabled = (context.scene.octane.hdr_tonemap_preview_enable and context.scene.octane.use_preview_setting_for_camera_imager)
        col.prop(oct_cam, "exposure")
        col.prop(oct_cam, "gamma")
        col.prop(oct_cam, "vignetting")
        col.prop(oct_cam, "saturation")
        col.prop(oct_cam, "white_saturation")
        col.prop(oct_cam, "hot_pix")
        col.prop(oct_cam, "min_display_samples")
        col.prop(oct_cam, "highlight_compression")
        col.prop(oct_cam, "max_tonemap_interval")
        col.prop(oct_cam, "dithering")
        col.prop(oct_cam, "premultiplied_alpha")
        col.prop(oct_cam, "neutral_response")
        col.prop(oct_cam, "disable_partial_alpha")
        #col.prop(oct_cam, "custom_lut")
        #col.prop(oct_cam, "lut_strength")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneManagePostprocess(Operator):
    bl_label = 'Post Processing'
    bl_idname = 'octane.manage_postprocess'
    bl_options = {'REGISTER', 'UNDO'}
    
    def draw(self, context):
        oct_cam = context.scene.oct_view_cam
        layout = self.layout
        col = layout.column(align=True)
        col.prop(context.scene.oct_view_cam, "postprocess", text="Enable Postprocess")
        col.prop(context.scene.octane, "use_preview_post_process_setting")
        col = layout.column(align=True)
        col.enabled = (context.scene.oct_view_cam.postprocess and context.scene.octane.use_preview_post_process_setting)
        col.prop(oct_cam, "cut_off")
        col.prop(oct_cam, "bloom_power")
        col.prop(oct_cam, "glare_power")
        col = layout.column(align=True)
        col.enabled = (context.scene.oct_view_cam.postprocess and context.scene.octane.use_preview_post_process_setting)
        col.prop(oct_cam, "glare_ray_count")
        col.prop(oct_cam, "glare_angle")
        col.prop(oct_cam, "glare_blur")
        col.prop(oct_cam, "spectral_intencity")
        col.prop(oct_cam, "spectral_shift")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneManageDenoiser(Operator):
    bl_label = 'AI Denoiser'
    bl_idname = 'octane.manage_denoiser'
    bl_options = {'REGISTER', 'UNDO'}
    
    def draw(self, context):
        oct_cam = context.scene.oct_view_cam
        view_layer = context.window.view_layer
        layout = self.layout
        col = layout.column(align=True)
        col.prop(oct_cam, 'enable_denoising', text='Enable Denosier')
        col.prop(view_layer, "use_pass_oct_denoise_beauty", text="Enable Beauty Pass")
        
        col = layout.column(align=True)
        col.enabled = (oct_cam.enable_denoising and view_layer.use_pass_oct_denoise_beauty)
        col.label(text="Spectral AI Denoiser")
        col.prop(oct_cam, 'denoise_volumes')
        col.prop(oct_cam, 'denoise_on_completion')
        col.prop(oct_cam, 'min_denoiser_samples')
        col.prop(oct_cam, 'max_denoiser_interval')
        col.prop(oct_cam, 'denoiser_blend')

        col = layout.column(align=True)
        col.enabled = (oct_cam.enable_denoising and view_layer.use_pass_oct_denoise_beauty)
        col.label(text="AI Up-Sampler")
        col.prop(oct_cam.ai_up_sampler, 'sample_mode')
        col.prop(oct_cam.ai_up_sampler, 'enable_ai_up_sampling')
        col.prop(oct_cam.ai_up_sampler, 'up_sampling_on_completion')
        col.prop(oct_cam.ai_up_sampler, 'min_up_sampler_samples')
        col.prop(oct_cam.ai_up_sampler, 'max_up_sampler_interval')

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneManagePasses(Operator):
    bl_label = 'Render Passes'
    bl_idname = 'octane.manage_render_passes'
    bl_options = {'REGISTER', 'UNDO'}

    passes: EnumProperty(items=[
        ('Beauty', 'Beauty', ''),
        ('Denoiser', 'Denoiser', ''),
        ('Post processing', 'Post processing', ''),
        ('Render layer', 'Render layer', ''),
        ('Lighting', 'Lighting', ''),
        ('Cryptomatte', 'Cryptomatte', ''),
        ('Info', 'Info', ''),
        ('Material', 'Material', ''),
    ], name='Passes', default='Beauty')
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        scene = context.scene
        rd = scene.render
        view_layer = context.view_layer
        octane_view_layer = view_layer.octane

        layout.prop(self, 'passes')
        layout.separator()

        if(self.passes == 'Beauty'):
            flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_beauty")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_emitters")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_env")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_sss")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_shadow")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_irradiance")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_dir")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_noise")      
            layout.row().separator()
            split = layout.split(factor=1)
            split.use_property_split = False
            row = split.row(align=True)
            row.prop(view_layer, "use_pass_oct_diff", text="Diffuse", toggle=True)
            row.prop(view_layer, "use_pass_oct_diff_dir", text="Direct", toggle=True)
            row.prop(view_layer, "use_pass_oct_diff_indir", text="Indirect", toggle=True)        
            row.prop(view_layer, "use_pass_oct_diff_filter", text="Filter", toggle=True)         
            layout.row().separator()
            split = layout.split(factor=1)
            split.use_property_split = False
            row = split.row(align=True)
            row.prop(view_layer, "use_pass_oct_reflect", text="Reflection", toggle=True)
            row.prop(view_layer, "use_pass_oct_reflect_dir", text="Direct", toggle=True)
            row.prop(view_layer, "use_pass_oct_reflect_indir", text="Indirect", toggle=True)        
            row.prop(view_layer, "use_pass_oct_reflect_filter", text="Filter", toggle=True)     
            layout.row().separator()
            split = layout.split(factor=1)
            split.use_property_split = False
            row = split.row(align=True)
            row.prop(view_layer, "use_pass_oct_refract", text="Refraction", toggle=True)
            row.prop(view_layer, "use_pass_oct_refract_filter", text="Refract Filter", toggle=True)
            layout.row().separator()
            split = layout.split(factor=1)
            split.use_property_split = False
            row = split.row(align=True)
            row.prop(view_layer, "use_pass_oct_transm", text="Transmission", toggle=True)
            row.prop(view_layer, "use_pass_oct_transm_filter", text="Transm Filter", toggle=True)        
            layout.row().separator()
            split = layout.split(factor=1)
            split.use_property_split = False
            row = split.row(align=True)
            row.prop(view_layer, "use_pass_oct_volume", text="Volume", toggle=True)
            row.prop(view_layer, "use_pass_oct_vol_mask", text="Mask", toggle=True)
            row.prop(view_layer, "use_pass_oct_vol_emission", text="Emission", toggle=True)        
            row.prop(view_layer, "use_pass_oct_vol_z_front", text="ZFront", toggle=True)
            row.prop(view_layer, "use_pass_oct_vol_z_back", text="ZBack", toggle=True)
        elif(self.passes == 'Denoiser'):
            flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_denoise_beauty", text="Beauty")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_denoise_diff_dir", text="DiffDir")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_denoise_diff_indir", text="DiffIndir")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_denoise_reflect_dir", text="ReflectDir")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_denoise_reflect_indir", text="ReflectIndir")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_denoise_emission", text="Emission")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_denoise_remainder", text="Remainder")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_denoise_vol", text="Volume")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_denoise_vol_emission", text="VolEmission")
        elif(self.passes == 'Post processing'):
            flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_postprocess", text="Post processing")
            col = flow.column()
            col.prop(octane_view_layer, "pass_pp_env")
        elif(self.passes == 'Render layer'):
            flow = layout.grid_flow(row_major=True, columns=3, even_columns=True, even_rows=False, align=False)
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_layer_shadows", text="Shadow")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_layer_black_shadow", text="BlackShadow")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_layer_reflections", text="Reflections")
        elif(self.passes == 'Lighting'):
            flow = layout.grid_flow(row_major=True, columns=3, even_columns=True, even_rows=False, align=False)
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_ambient_light", text="Ambient")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_ambient_light_dir", text="Direct")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_ambient_light_indir", text="Indirect")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_sunlight", text="Sunlight")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_sunlight_dir", text="Direct")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_sunlight_indir", text="Indirect")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_pass_1", text="Light Pass 1")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_dir_pass_1", text="Direct")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_indir_pass_1", text="Indirect")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_pass_2", text="Light Pass 2")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_dir_pass_2", text="Direct")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_indir_pass_2", text="Indirect")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_pass_3", text="Light Pass 3")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_dir_pass_3", text="Direct")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_indir_pass_3", text="Indirect")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_pass_4", text="Light Pass 4")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_dir_pass_4", text="Direct")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_indir_pass_4", text="Indirect")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_pass_5", text="Light Pass 5")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_dir_pass_5", text="Direct")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_indir_pass_5", text="Indirect")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_pass_6", text="Light Pass 6")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_dir_pass_6", text="Direct")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_indir_pass_6", text="Indirect")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_pass_7", text="Light Pass 7")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_dir_pass_7", text="Direct")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_indir_pass_7", text="Indirect")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_pass_8", text="Light Pass 8")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_dir_pass_8", text="Direct")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_light_indir_pass_8", text="Indirect")
        elif(self.passes == 'Cryptomatte'):
            flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_crypto_instance_id", text="Instance ID")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_crypto_mat_node_name", text="MatNodeName")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_crypto_mat_node", text="MatNode")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_crypto_mat_pin_node", text="MatPinNode")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_crypto_obj_node_name", text="ObjNodeName")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_crypto_obj_node", text="ObjNode")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_crypto_obj_pin_node", text="ObjPinNode")
            layout.row().separator()
            row = layout.row(align=True)
            row.prop(octane_view_layer, "cryptomatte_pass_channels")
            row = layout.row(align=True)
            row.prop(octane_view_layer, "cryptomatte_seed_factor")
        elif(self.passes == 'Info'):
            flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_info_z_depth")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_info_position")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_info_uv")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_info_tex_tangent")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_info_motion_vector")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_info_mat_id")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_info_obj_id")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_info_obj_layer_color")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_info_baking_group_id")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_info_light_pass_id")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_info_render_layer_id")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_info_render_layer_mask")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_info_wireframe")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_info_ao")
            layout.row().separator()
            split = layout.split(factor=0.15)
            split.use_property_split = False
            split.label(text="Normal")
            row = split.row(align=True)       
            row.prop(view_layer, "use_pass_oct_info_geo_normal", text="Geometric", toggle=True)         
            row.prop(view_layer, "use_pass_oct_info_smooth_normal", text="Smooth", toggle=True)
            row.prop(view_layer, "use_pass_oct_info_shading_normal", text="Shading", toggle=True)
            row.prop(view_layer, "use_pass_oct_info_tangent_normal", text="Tangent", toggle=True)
            layout.row().separator()
            row = layout.row(align=True)
            row.prop(octane_view_layer, "info_pass_max_samples")
            row = layout.row(align=True)
            row.prop(octane_view_layer, "info_pass_sampling_mode")
            row = layout.row(align=True)
            row.prop(octane_view_layer, "info_pass_z_depth_max")
            row = layout.row(align=True)
            row.prop(octane_view_layer, "info_pass_uv_max")
            row = layout.row(align=True)
            row.prop(octane_view_layer, "info_pass_uv_coordinate_selection")
            row = layout.row(align=True)
            row.prop(octane_view_layer, "info_pass_max_speed")
            row = layout.row(align=True)
            row.prop(octane_view_layer, "info_pass_ao_distance")                        
            row = layout.row(align=True)
            row.prop(octane_view_layer, "info_pass_alpha_shadows") 
        elif(self.passes == 'Material'):
            flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_mat_opacity")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_mat_roughness")
            col = flow.column()
            col.prop(view_layer, "use_pass_oct_mat_ior")

            layout.row().separator()

            split = layout.split(factor=0.15)
            split.use_property_split = False
            split.label(text="Filter")
            row = split.row(align=True)       
            row.prop(view_layer, "use_pass_oct_mat_diff_filter_info", text="Diffuse", toggle=True)         
            row.prop(view_layer, "use_pass_oct_mat_reflect_filter_info", text="Reflection", toggle=True)
            row.prop(view_layer, "use_pass_oct_mat_refract_filter_info", text="Refraction", toggle=True)
            row.prop(view_layer, "use_pass_oct_mat_transm_filter_info", text="Transmission", toggle=True)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OctaneManageLayers(Operator):
    bl_label = 'Render Layers'
    bl_idname = 'octane.manage_render_layers'
    bl_options = {'REGISTER', 'UNDO'}
    
    def draw(self, context):
        s_octane = context.scene.octane
        layout = self.layout
        col = layout.column(align=True)
        col.prop(s_octane, "layers_enable", text="Enable Render Layers")
        col = layout.column(align=True)
        col.enabled = s_octane.layers_enable
        col.prop(s_octane, "layers_mode")
        col.prop(s_octane, "layers_current")
        col.prop(s_octane, "layers_invert")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)