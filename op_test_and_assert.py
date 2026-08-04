import bpy
from .common import split_object_name as son, list_names, copy_armature, get_bone_chain, select_bones
from .common import dnd, div, br, bl, keep_composer



class ARMATURE_OT_drig_test_function(bpy.types.Operator):
    bl_idname = "armature.drig_test_function"
    bl_label = "Test Function"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):

        decomposer = context.object
        base = decomposer.drig_base

        for bone in decomposer.pose.bones:
            for constraint in bone.constraints:
                if constraint.name.split(bl)[0] == 'FUNCTION':
                    print('Function found!')
                    # okay finally works.
                    # constraints should take precedent over the cuprop, right?
                    # so composition needs to account for them
                    # lets not get bogged down by this though
                    # we need to get decomp to match BASE first
                    # then worry about recomp

        edit_property_list = []
        for attr in bpy.types.EditBone.bl_rna.properties.items():
            if attr[0] in ['name', 'rna_type', 'collections']: continue
            if attr[0] in ['select', 'select_tail', 'select_head']: continue
            edit_property_list.append(attr[0])

        pose_property_list = []
        for attr in bpy.types.PoseBone.bl_rna.properties.items():
            if attr[0] in ['name', 'rna_type', 'collections']: continue
            if attr[0] in ['select', 'select_tail', 'select_head']: continue
            # Idk if the others are even necessary. This one breaks stuff
            # But previous me had a cryptic if statement about using it...?
            pose_property_list.append(attr[0])

        def compare_settings_EDIT(base, decomp):

            for prop in edit_property_list:
                if base.is_property_readonly(prop): continue
                # this is stupid but i cant find a way to check if a type is subscriptable
                # aka something that can be accessed with []. 
                # Which we need to do or it doesnt print the internal values
                if (
                    isinstance(getattr(base, prop), float) or 
                    isinstance(getattr(base, prop), bool) or
                    isinstance(getattr(base, prop), int) or
                    getattr(base, prop) == None
                ):
                    if getattr(base, prop) != getattr(decomp, prop):
                        print(prop)
                        print(getattr(base, prop), getattr(decomp, prop))
                        

                elif getattr(base, prop)[:] != getattr(decomp, prop)[:]:
                    print(prop)
                    print(getattr(base, prop)[:], getattr(decomp, prop)[:])



        def compare_settings_POSE(base, decomp):

            for prop in pose_property_list:
                if base.is_property_readonly(prop): continue

                if (
                    isinstance(getattr(base, prop), float) or 
                    isinstance(getattr(base, prop), bool) or
                    getattr(base, prop) == None
                ):
                    if getattr(base, prop) != getattr(decomp, prop):
                        print(getattr(base, prop), getattr(decomp, prop))
                        print("no index")
                        

                elif getattr(base, prop)[:] != getattr(decomp, prop)[:]:
                    print(getattr(base, prop)[:], getattr(decomp, prop)[:])
                    print("index")
                    if prop == 'bbone_use_scale_start':
                        print("found")

        for name in list_names(decomposer.data.collections_all[dnd['base_set']].bones_recursive):
            #Why is it not selecting base...
            bpy.ops.object.mode_set(mode='OBJECT')
            decomposer.select_set(True)
            bpy.data.objects[decomposer.name].select_set(True)
            base.select_set(True)
            bpy.data.objects[base.name].select_set(True)
            bpy.ops.object.mode_set(mode='EDIT')

            # Doesnt work with components! At least I think thats the issue
            # Really we should make this check if the same bone even exists
            # and account for BASE potentially actually having the BASE prefix lol
            bs_bone = base.data.edit_bones[name.split(div)[1]]
            ds_bone = decomposer.data.edit_bones[name]
            compare_settings_EDIT(bs_bone, ds_bone)
            bpy.ops.object.mode_set(mode='POSE')
            bs_bone = base.pose.bones[name.split(div)[1]]
            ds_bone = decomposer.pose.bones[name]
            compare_settings_POSE(bs_bone, ds_bone)
            bpy.ops.object.mode_set(mode='OBJECT')
            # go through each's properties and make sure they're identical
            # print any that arent
        


        return {'FINISHED'}



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
        bpy.ops.armature.drig_compose()
        bpy.ops.armature.drig_decompose()
        decomposer = bpy.data.objects[f"{dnd['decomposer']}{div}{son(base, 1)}"]

        return {'FINISHED'}



classes = [ARMATURE_OT_drig_test_function, ARMATURE_OT_drig_assert_base_matches_decomposer]

def register():
    for cls in classes: bpy.utils.register_class(cls)

def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)

