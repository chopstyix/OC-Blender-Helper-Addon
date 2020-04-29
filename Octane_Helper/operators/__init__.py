from .materials import *
from .environments import *
from .backplates import *
from .lights import *
from .render import *
from .windows import *
from .presets import *

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
    OctaneAddTexEnv,
    OctaneAddSkyEnv,
    OctaneAddMedEnv,
    OctaneChangeRenderID,
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
    OctaneAddLightSpot,
    OctaneAddLightToonPoint,
    OctaneAddLightToonSpot,
    OctaneChangeObjProperties,
    OctaneCopyObjProperties,
    OctaneEnvironmentsManager,
    OctaneActivateEnvironment,
    OctaneRenameEnvironment,
    OctaneDeleteEnvironment,
    OctanePresetsManager
)

def register_operators():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister_operators():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)