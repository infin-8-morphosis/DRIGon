import bpy
from .common import split_object_name as son, list_names, copy_armature, get_bone_chain, select_bones
from .common import dnd, div, br, bl, keep_composer



class ARMATURE_OT_drig_assert_base_matches_decomposer(bpy.types.Operator):
    bl_idname = "armature.drig_assert_base_matches_decomposer"
    bl_label = "Base matches Decomposer?"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):

        # Check if base is selected if you want this test to be available
        # on the main panel
        # Run all the operations in order
        # Compose, Finalise, Decompose
        # Then compare DECOMPOSER to BASE
        # They should be identical since nothing has been done.
        # Oh, this will catch redundancies introduced by decomp and
        # then we can account for them.

        base = context.object
        print(context.object)
        bpy.ops.armature.drig_compose()
        bpy.ops.armature.drig_decompose()
        decomposer = bpy.data.objects[f"{dnd['decomposer']}{div}{son(base, 1)}"]
        print(decomposer.name)

        return {'FINISHED'}



classes = [ARMATURE_OT_drig_assert_base_matches_decomposer]

def register():
    for cls in classes: bpy.utils.register_class(cls)

def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)

