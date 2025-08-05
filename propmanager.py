import bpy #type:ignore

# Scene 
#---------------------------------------------------------------------------------------------------
drig_comp_operators = [("INIT", "Initialise", ""),
                ("PREP_BASE", "Prepare Base", ""),
                ("COMP_SET", "Compose Set", ""),
                ("EQUIV_CHAIN", "Equivalent Chains", "")]

bpy.types.Scene.drig_morph_select = bpy.props.PointerProperty(type=bpy.types.Armature)

# Object 
#---------------------------------------------------------------------------------------------------
bpy.types.Object.drig_base = bpy.props.PointerProperty(type=bpy.types.Object)
bpy.types.Object.drig_target_main = bpy.props.PointerProperty(type=bpy.types.Object)
bpy.types.Object.drig_fate = bpy.props.StringProperty()
bpy.types.Object.drig_subtarget_dict = {}

# Armature
#---------------------------------------------------------------------------------------------------
bpy.types.Armature.drig_morph_parent = bpy.props.PointerProperty(type=bpy.types.Armature)

# Bone Collections
#---------------------------------------------------------------------------------------------------
parent_types = [("KEEP", "Keep", ""),
                ("EQUIV", "Equivalent", ""),
                ("EQUIV_PARENT", "Equivalent's Parent", ""),
                ("EQUIV_CHAIN", "Equivalent Chains", "")]
bpy.types.BoneCollection.drig_parent_method = bpy.props.EnumProperty(
    items=parent_types, 
    description="Choose to keep parenting as-is, or change it")

trans_types = [("NONE", "None", ""),
               ("TRANSFORMS", "All Transforms", ""),
               ("LOCATION", "Location", ""),
               ("ROTATION", "Rotation", ""),
               ("SCALE", "Scale", "")]
bpy.types.BoneCollection.drig_trans_type = bpy.props.EnumProperty(
    items=trans_types, 
    description="Adds constraints to this set, copying the transforms of the chosen set")

bpy.types.BoneCollection.drig_trans_target = bpy.props.StringProperty()
bpy.types.BoneCollection.drig_set_deform = bpy.props.BoolProperty()

# Bones
#---------------------------------------------------------------------------------------------------
function_types = [("NONE", "None", ""),
                   ("IK_BASIC", "Basic IK", ""),
                   ("IK_POLES", "Poled IK", ""),
                   ("CHAIN", "Chain", "Apply a chain of inherited rotations")]
bpy.types.Bone.drig_function_type = bpy.props.EnumProperty(
    items=function_types,
    description="Add functionality to a chain of bones")
bpy.types.Bone.drig_function_set = bpy.props.StringProperty()

bpy.types.Bone.drig_component_target = bpy.props.PointerProperty(type=bpy.types.Object)
bpy.types.Bone.drig_component_set = bpy.props.StringProperty()
bpy.types.Bone.drig_component_connected = bpy.props.BoolProperty(
    description="Connects the bone at the origin point to the overlapping bone in the main armature, if one is present")
#---------------------------------------------------------------------------------------------------

classes = []

def register():
    for cls in classes: bpy.utils.register_class(cls)
def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)