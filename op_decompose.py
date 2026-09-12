import bpy
from .composition import *
from .common import split_object_name as son, copy_armature

# TODO:
# In theory this will all be in reverse, right?
# For now, assume BASE is still in sync. In future it should be able to be reconstructed
# That should be step one actually
# No. You need to make a DECOMPOSER also even firstier
            # DONE / UNNECESSARY
            # 1. Make DECOMPOSER
                # Basically just a copy of RIG
            # 2. Reconstruct BASE
                # Ignore IK bones. Go through bones, add unique names without IK to a list
                # Remove any repeats. See if any of the bone groups only contains bones with those names...?
                # I'll be honest maybe BASE should just be kept... 
            # 3. IK / Functions
                # Go through all bones for IK's and get_parent until you locate a matching function.
                # Copy the IK to the function bone and deactivate it / name it appropriately.
                # If there is no funcbone, either leave it or assume the closest unconnected parent is 
                # where it should go.
# 4. Constraints
    # Add them to BASE, idk more details

# 4. Decompose Sets
    # Lets assume we're rebuilding COMPOSITION_SETS.
    # Cycle through all bones, have a list of prefixes
    # make comp sets, add sets, assign equiv BASE bones to the sets.
    # Delete all non-BASE/IK bones
    # Really poles and such should be part of base in some way to prevent confusion here...
# # 5. Components
#     for constraint in bone.constraints:
#         if constraint.name.split(1, bl) == 'CONSTRAINT':
#             select child of bone recursively, 
#             (make drig_component_set into drig_component_root? We havent used it at all...)
    # The constraint is already there to tell us where to separate
    # The constraint is on the bone the component is attached to...
    # But what if theres multiple children...? Shouldnt it 
    # Ah, but no guarantee theres a single parent either...
    # This relies on BASE having been isolated
    # Priority order:
        # If the bone has a connected child, select recursive children of that child
        # If no bone is connected, assume all children are part of the component
        # UNLESS those children are part of IK, in which ignore them?
# Should make some kind of comparer to check if the BASE is actually identical 
# to itself unedited

# If we get a good rig comparer built, we should remove any redundant constraints
# For things that will be replicated anyway via the bone functions
# Unsure how exactly you'd determine if they're redundant tbh

class ARMATURE_OT_drig_decompose(bpy.types.Operator):
    bl_idname = "armature.drig_decompose"
    bl_label = "Decompose to Base"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):

        rig = context.object # Selection: RIG
        decomposer = copy_armature(rig, dnd['decomposer'], 'FINALISE')
        decomposer.data = rig.data.copy()
        context.collection.objects.link(decomposer)


        def remove_IK_bones_EDIT():
            assert bpy.context.mode == 'EDIT_ARMATURE', "Not in EDIT mode!"

            chopping_block = []
            for bone in decomposer.data.edit_bones:
                print(bone)
                if son(bone, 0) == dnd['ik']:
                    chopping_block.append(bone)
            for bone in chopping_block:
                    decomposer.data.edit_bones.remove(bone)


        def transfer_function_constraint(function):

            pose_bones = decomposer.pose.bones
            if function == 'IK_BASIC':
                # Funnily the pose.bone and data.bone uses here are necessary
                ik_equiv = decomposer.data.bones[f"{dnd['ik']}{div}{son(bone, -1)}"]
                chainbase = pose_bones[get_bone_chain(ik_equiv)[0]]
                if ik_constraint := chainbase.constraints.get(dnd['ik']):
                    # Interesting. The copy actually sets it to the deleted IK bone...
                    # ...which throws up an error in the terminal, which may annoy someone, though it is convenient.
                    ik_name = f"FUNCTION{bl}{chainbase.name}{br}"
                    # Want to not use div here, should warn to not use []? 
                    base_constraints = pose_bones[bone.name].constraints
                    if ik_already_present := base_constraints.get(ik_name):
                        base_constraints.remove(ik_already_present)
                        # add a function to common to copy settings...?
                    new_ik = base_constraints.copy(ik_constraint)
                    new_ik.name = ik_name
                    new_ik.mute = True
                    new_ik.target = rig # This is to remove the terminal error

        for bone in decomposer.data.bones:
            if bone.drig_function_type != 'NONE':
                transfer_function_constraint(bone.drig_function_type)

        rig.select_set(False) # Selection: None
        decomposer.select_set(True)  # Selection: DECOMPOSER
        bpy.ops.object.mode_set(mode='EDIT')
        remove_IK_bones_EDIT()
        bpy.ops.object.mode_set(mode='OBJECT')

        
        # bpy.ops.armature.separate()


        return {'FINISHED'}



classes = [ARMATURE_OT_drig_decompose]

def register():
    for cls in classes: bpy.utils.register_class(cls)
def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)