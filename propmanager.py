import bpy
bt, bp = bpy.types, bpy.props

# Scene 
#---------------------------------------------------------------------------------------------------
drig_comp_operators =          [("INIT", "Initialise", ""),
                                ("PREP_BASE", "Prepare Base", ""),
                                ("COMP_SET", "Compose Set", ""),
                                ("EQUIV_CHAIN", "Equivalent Chains", "")]

bt.Scene.drig_morph_select =    bp.PointerProperty(type=bt.Armature)

# Object 
#---------------------------------------------------------------------------------------------------
bt.Object.drig_base =           bp.PointerProperty(type=bt.Object)
bt.Object.drig_target_main =    bp.PointerProperty(type=bt.Object)
bt.Object.drig_fate =           bp.StringProperty()
bt.Object.drig_subtarget_dict = {}

# Armature
#---------------------------------------------------------------------------------------------------
bt.Armature.drig_morph_parent = bp.PointerProperty(type=bt.Armature)

# Bone Collections
#---------------------------------------------------------------------------------------------------
parent_methods =                       [("KEEP", "Keep", ""),
                                        ("EQUIV", "Equivalent", ""),
                                        ("EQUIV_PARENT", "Equivalent's Parent", ""),
                                        ("EQUIV_CHAIN", "Equivalent Chains", "")]
bt.BoneCollection.drig_parent_method =  bp.EnumProperty(
    items=parent_methods, 
    description="Choose to keep parenting as-is, or change it")

trans_types =                          [("NONE", "None", ""),
                                        ("TRANSFORMS", "All Transforms", ""),
                                        ("LOCATION", "Location", ""),
                                        ("ROTATION", "Rotation", ""),
                                        ("SCALE", "Scale", "")]
bt.BoneCollection.drig_trans_type =     bp.EnumProperty(
    items=trans_types, 
    description="Adds constraints to this set, copying the transforms of the chosen set")
bt.BoneCollection.drig_trans_target =   bp.StringProperty()

bt.BoneCollection.drig_set_deform =     bp.BoolProperty()

# Bones
#---------------------------------------------------------------------------------------------------
bt.Bone.drig_function_set =         bp.StringProperty()
function_types =                   [("NONE", "None", ""),
                                    ("IK_BASIC", "Basic IK", ""),
                                    ("IK_POLES", "Poled IK", ""),
                                    ("CHAIN", "Chain", "Apply a chain of inherited rotations")]
bt.Bone.drig_function_type =        bp.EnumProperty(
    items=function_types,
    description="Add functionality to a chain of bones")

bt.Bone.drig_chain_amount =         bp.IntProperty(default=1, min=1, soft_max=10)
chain_types =                      [("SINGLE", "Single", "Leave the bone as a single bone"),
                                    ("SPLIT", "Split", "Divide into a chain of equally-sized bones"),
                                    ("RECURSIVE", "Recursive", "Divide into a chain of progressively smaller bones"),
                                    ("JOINT", "Joint", "Divide in two, with a configured 'elbow' between")]
bt.Bone.drig_chain_type =           bp.EnumProperty(
    items=chain_types,
    description="Divide a bone into a chain of bones")

bt.Bone.drig_component_target =     bp.PointerProperty(type=bt.Object)
bt.Bone.drig_component_set =        bp.StringProperty()
bt.Bone.drig_component_connected =  bp.BoolProperty(
    description="Connects the bone at the origin point to the overlapping bone in the main armature, if one is present")
#---------------------------------------------------------------------------------------------------

classes = []

def register():
    for cls in classes: bpy.utils.register_class(cls)
def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)