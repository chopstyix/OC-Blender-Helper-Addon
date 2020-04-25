from .materials import *
from .environment import *
from .render import *

classes = (
    OctaneAssignUniversal,
    OctaneAssignDiffuse,
    OctaneAssignEmissive,
    OctaneAssignColorgrid,
    OctaneAssignUVgrid,
    OctaneAssignGlossy,
    OctaneAssignSpecular,
    OctaneAssignMix,
    OctaneAssignPortal,
    OctaneAssignShadowCatcher,
    OctaneAssignToon,
    OctaneAssignMetal,
    OctaneAssignLayered,
    OctaneAssignComposite,
    OctaneAssignHair,
    OctaneAssignSSS,
    OctaneRenameMat,
    OctaneCopyMat,
    OctanePasteMat,
    OctaneSetupHDRIEnv,
    OctaneSetRenderID,
    OctaneTransformHDRIEnv,
    OctaneOpenCompositor,
    OctaneToggleClayMode,
    OctaneAddBackplate,
    OctaneRemoveBackplate,
    OctaneModifyBackplate,
    OctaneManagePostprocess,
    OctaneManageImager,
    OctaneManageDenoiser,
    OctaneManageLayers,
    OctaneManagePasses,
    OctaneAutosmooth,
    OctaneLightsManager,
    OctaneSetLight,
    OctaneCamerasManager,
    OctaneCopyCameraSettings,
    OctaneCopyPostProcessSettings,
    OctaneCopyDenosierSettings,
    OctaneAddLightSphere,
    OctaneAddLightArea,
    OctaneAddLightToon
)

def register_operators():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister_operators():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)