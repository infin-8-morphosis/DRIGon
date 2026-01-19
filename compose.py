import bpy, mathutils #type:ignore
from .common import split_name, list_names, copy_armature, get_bone_chain, select_bones
from .common import dnd, div, br, bl, keep_composer


class ARMATURE_OT_drig_compose(bpy.types.Operator):
    bl_idname = "armature.drig_compose"
    bl_label = "Compose to Composer"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        def compose_bone(bone, set):
            bpy.ops.object.mode_set(mode='EDIT')
            dupe = duplicate_bone_EDIT(composer.data, bone, set)
            dupe.parent = determine_parent_EDIT(composer.data, dupe.name, set)
            dupename = dupe.name
            bpy.ops.object.mode_set(mode='OBJECT')
            g = composer.data.bones.get(dupename)
            set.assign(composer.data.bones[dupename])
            if set.drig_trans_type != 'NONE':
                add_trans_constraints(composer, dupename, set)
            composer.data.bones[dupename].use_deform = set.drig_set_deform
            # Set all base_set bones to be non-deforming?

        def compose_set(composer, set):
            if set.name != dnd['base_set']:
                bpy.ops.object.mode_set(mode='OBJECT')
                bone_list = list_names(set.bones)
                for bone in bone_list:
                    compose_bone(bone, set)
            if set.children: 
                for child in set.children:
                    compose_set(composer, child)

        def process_chain_EDIT(composer, bone):
            if bone.drig_chain_type == 'SPLIT':
                bpy.ops.armature.subdivide(number_cuts = bone.drig_chain_amount)
                

        # Copies base, adds new armature, removes all bones from bone groups, except COMPOSITION_SETS.
        # This is where components are joined. Should that be separated too?
        def make_composer():

            # Uses a constraint to save the orientation of the component
            # To be used later when decomposing back to separate pieces
            def save_transform(object, bone_name, component, original):
                transform = object.pose.bones[bone_name].constraints.new('TRANSFORM')
                transform.name = f"COMPONENT{bl}{original.name}{br}"
                transform.mute = True
                transform.from_min_x = component.location.x
                transform.from_min_y = component.location.y
                transform.from_min_z = component.location.z
                transform.from_min_x_rot = component.rotation_euler.x
                transform.from_min_y_rot = component.rotation_euler.y
                transform.from_min_z_rot = component.rotation_euler.z
                transform.from_min_x_scale = component.scale.x
                transform.from_min_y_scale = component.scale.y
                transform.from_min_z_scale = component.scale.z
                transform = mathutils.Vector((round(transform.from_min_x, 2),
                                            round(transform.from_min_y, 2),
                                            round(transform.from_min_z, 2)))

                return transform
            
            def merge_component(base, component_list):
                for name in component_list: 
                    bone = base.data.bones[name]
                    bpy.data.objects[bone.drig_component_target.name].select_set(False)
                    original = bone.drig_component_target
                    component = original.copy()
                    component.data = original.data.copy()
                    context.collection.objects.link(component)
                    transform = save_transform(composer, bone.name, component, original)
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.data.objects[component.name].select_set(True)
                    context.view_layer.objects.active = composer
                    bpy.ops.object.join()

                for name in component_list:
                # This is separate presumably to reduce redundant bone checks?
                # Assumes no overlapping bones!
                # use the transform to join the component base to the component parent bone.
                    master_set = composer.data.collections_all[dnd['master_set']]
                    for each in master_set.bones_recursive:
                        if each.head_local == transform: # TODO: Minus component transform so this works outside 0,0,0
                            bpy.ops.object.mode_set(mode='EDIT')
                            e_bones = composer.data.edit_bones
                            e_bones[each.name].parent = e_bones[name]
                            e_bones[each.name].use_connect = True # Not always wanted!
                            bpy.ops.object.mode_set(mode='OBJECT')
                            break

            # Selection: Base
            base = context.object.drig_base 
            composer = copy_armature(base, dnd['composer'], 'FINALISE', keep_composer)
            composer.data = base.data.copy()
            composer.drig_base = base
            cd = composer.data
            bd = base.data
            sn = split_name
            cd.name = f"{dnd['composer']}{div}{sn(composer,1)}{div}{sn(bd,-1)}"

            bpy.data.objects[base.name].select_set(False)
            component_list = []

            for bone in bd.collections_all[dnd['master_set']].bones_recursive:
                if bone.drig_component_target:
                    component_list.append(bone.name)
            
            merge_component(base, component_list)

            for bone in cd.collections_all[dnd['master_set']].bones_recursive:
                bone.name = f"{dnd['base']}{div}{bone.name}"
                bone.use_deform = False

            return composer

        # Selection: Base
        composer = make_composer() 
        base = context.object.drig_base
        # ^ Components are joined here. 
        composer.select_set(True) # Selected: Composer | Selection: Composer, Base
        base.select_set(False) #Deselected: Base | Selection: Composer
        context.view_layer.objects.active = composer
        comp_set = composer.data.collections_all[dnd['master_set']]

        if not composer.data.collections_all.get(dnd['base_set']):
            base_set = composer.data.collections.new(dnd['base_set'],parent=comp_set)
        for bone in comp_set.bones_recursive:
            composer.data.collections_all[dnd['base_set']].assign(bone)
        
        for bone in base_set.bones: # Add chains here?
            if bone.drig_chain_type != 'SINGLE':
                bpy.ops.object.mode_set(mode='EDIT')
                select_bones(False, composer, 'EDIT') # I swear that last parameter isnt used
                composer.data.edit_bones.active = composer.data.edit_bones[bone.name]
                process_chain_EDIT(composer, bone)
                bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.mode_set(mode='EDIT')
        for set in comp_set.children: 
            compose_set(composer, set)

        # Why does this need to be in edit mode?
        for bone in base_set.bones:
            if bone.drig_function_type != 'NONE':
                add_drig_function(composer, bone.name)
            # if bone.drig_component_target:
            #     join_drig_component(context, composer, bone.name)
        bpy.ops.object.mode_set(mode='OBJECT')

        composer.drig_fate = 'FINALISE'

        return {'FINISHED'}


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
# 5. Components
    # The constraint is already there to tell us where to separate
    # The constraint is on the bone the component is attached to...
    # But what if theres multiple children...? Shouldnt it 
    # Ah, but no guarantee theres a single parent either...
    # This relies on BASE having been isolated
    # Priority order:
        # If the bone has a connected child, select recursive children of that child
        # If no bone is connected, assume all children are part of the component
        # UNLESS those children are part of IK, in which ignore them?
# Should make some kind of comparer to check if the BASE is actually identical to itself unedited
class ARMATURE_OT_drig_decompose(bpy.types.Operator):
    bl_idname = "armature.drig_decompose"
    bl_label = "Decompose to Base"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):
        rig = context.object # Selection: RIG
        decomposer = copy_armature(rig, dnd['decomposer'], 'FINALISE', keep_composer)
        decomposer.data = rig.data.copy()

        def remove_IK_bones_EDIT():
            chopping_block = []
            for bone in decomposer.data.edit_bones:
                if split_name(bone, 0) == dnd['ik']:
                    chopping_block.append(bone)
            for bone in chopping_block:
                    decomposer.data.edit_bones.remove(bone)

        def transfer_function_constraint(function):
            pobes = decomposer.pose.bones
            if function == 'IK_BASIC':
                # Funnily the pose.bone and data.bone uses here are necessary
                ik_equiv = decomposer.data.bones[f"{dnd['ik']}{div}{split_name(bone, -1)}"]
                chainbase = pobes[get_bone_chain(ik_equiv)[0]]
                if ik_constraint := chainbase.constraints.get(dnd['ik']):
                    # Interesting. The copy actually sets it to the deleted IK bone...
                    # ...which throws up an error in the terminal, which may annoy someone, though it is convenient.
                    ik_name = f"FUNCTION{bl}{chainbase.name}{br}"
                    # Want to not use div here, should warn to not use []? 
                    base_contraints = pobes[bone.name].constraints
                    if ik_already_present := base_contraints.get(ik_name):
                        base_contraints.remove(ik_already_present)
                        # add a function to common to copy settings...?
                    new_ik = base_contraints.copy(ik_constraint)
                    new_ik.name = ik_name
                    new_ik.target = rig # This is to remove the terminal error

        for bone in decomposer.data.bones:
            if bone.drig_function_type != 'NONE':
                transfer_function_constraint(bone.drig_function_type)

        bpy.ops.object.mode_set(mode='EDIT')
        remove_IK_bones_EDIT()
        bpy.ops.object.mode_set(mode='OBJECT')
        #bpy.ops.armature.separate()

        return {'FINISHED'}

# Make a separate one for decomp? Or just get it to check the name of the object?
class ARMATURE_OT_drig_finalise(bpy.types.Operator):
    bl_idname = "armature.drig_finalise"
    bl_label = "Finalise"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):
        
        composer = context.object # Selection: Composer
        base = composer.drig_base
        # At some point this will have a function to do this per morph.
        if base.drig_target_main:
            target = base.drig_target_main
        else:
            bpy.ops.armature.drig_make_target()
            target = bpy.data.objects[f"{dnd['target']}{div}{split_name(composer,1)}"]
            composer.drig_target_main = target
            base.drig_target_main = target
        target.select_set(True) # Seleced: RIG | Selection: Comp, RIG
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in composer.data.bones:
            transfer_bone_EDIT(composer, target, bone.name)
        # for bone in composer
        # make new bone with matching matrix

        # copy bones from composer to target in ONE edit mode
        return {'FINISHED'}


def map_bone_settings(target, base, final):
        if final:
            pass
            # target.use_connect = base.use_connect
        target.head = base.head
        target.tail = base.tail
        target.matrix = base.matrix

        target.parent = base.parent
        target.inherit_scale = base.inherit_scale
        target.use_deform = base.use_deform
        target.bbone_segments = base.bbone_segments
        target.bbone_rollout = base.bbone_rollout
        target.bbone_rollin = base.bbone_rollin
        target.bbone_easein = base.bbone_easein
        target.bbone_easeout = base.bbone_easeout
        target.bbone_x = base.bbone_x
        target.bbone_z = base.bbone_z
        target.bbone_handle_type_start = base.bbone_handle_type_start
        target.bbone_custom_handle_start = base.bbone_custom_handle_start
        target.bbone_handle_type_end = base.bbone_handle_type_end
        target.bbone_custom_handle_end = base.bbone_custom_handle_end

def transfer_bone_EDIT(composer, target, bone_name):
    if (e_bones := target.data.edit_bones).get(bone_name):
        targbone = e_bones[bone_name]
    else:
        targbone = e_bones.new(bone_name)
    compbone = composer.data.edit_bones[bone_name]
    map_bone_settings(targbone, compbone, True)

def duplicate_bone_EDIT(armature, bone_name, set):
    copy_name = f"{set.name}{div}{bone_name.split(div)[-1]}"
    copy = armature.edit_bones.new(copy_name)
    # if bone_name.split('.')[-1] == '.001':
    #     copy.name.removesuffix('.002')
    # else:
    copy.name.removesuffix('.001')
    map_bone_settings(copy, armature.edit_bones[bone_name], False)
    return copy

def determine_parent_EDIT(armature, bone_name, set):

    def parent_as_kept():
        if bep := base_equiv.parent:
            kept = armature.edit_bones[f"{set.name}{div}{split_name(bep,-1)}"]
        else:
            kept = None
        armature.edit_bones[bone_name].use_connect = connect
        return kept

    def parent_as_equivalent():
        if (pset := set.parent.name) == dnd['master_set']:
            equiv = None
        else:
            equiv = armature.edit_bones[f"{pset}{div}{bone_name.split(div)[-1]}"]
        return equiv

    method = set.drig_parent_method
    base_equiv = armature.edit_bones[f"{dnd['base_set']}{div}{bone_name.split(div)[-1]}"]
    connect = base_equiv.use_connect
    if method ==   'KEEP':              return parent_as_kept()
    elif method == 'EQUIV':             return parent_as_equivalent()
    elif method == 'EQUIV_PARENT':      return parent_as_equivalent().parent
    elif method == 'EQUIV_CHAIN':
        if not base_equiv.use_connect:       return parent_as_equivalent()
        if base_equiv.use_connect:           return parent_as_kept()

def add_trans_constraints(object, bone_name, set):
    type = f'COPY_{set.drig_trans_type}'
    constraint = object.pose.bones[f"{bone_name}"].constraints.new(type)
    constraint.target = object
    if dtt := set.drig_trans_target:
        constraint.subtarget = f"{dtt}{div}{bone_name.split(div)[-1]}"
    else:
        constraint.subtarget = f"{set.parent.name}{div}{bone_name.split(div)[-1]}"
    #alter constraint settings here

def add_drig_function(object, bone_name):

    def add_ik_target_EDIT(object, ik, chain):
        bpy.ops.object.mode_set(mode='EDIT')
        select_bones(False, object, 'EDIT') # Deselected: All Bones 
        bones_EDIT = object.data.edit_bones
        bones_EDIT[chain[0]].select_tail = True # Selected: End bone
        bpy.ops.armature.extrude_move(TRANSFORM_OT_translate={
            "value":(0, 1, 0),
            "orient_type":'NORMAL',
            "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1))}) # Selected: IK Bone | IK Bone, End Bone
        ik_bone_name = bpy.context.active_bone.name 
        bones_EDIT[ik_bone_name].use_connect = False
        bones_EDIT[ik_bone_name].parent = None # bones_EDIT[chain[-1]].parent
        bpy.ops.object.mode_set(mode='POSE')
        bones_POSE = object.pose.bones
        ik.target = object
        ik.subtarget = bones_POSE[ik_bone_name].name
        object.data.collections_all[dnd['master_set']].assign(bones_POSE[ik_bone_name])
        # This won't work if the constraint name isn't known...
        select_bones(False, object, 'EDIT') # Deselected: All Bones

    bone = object.data.bones[bone_name]
    set = object.data.collections_all.get(bone.drig_function_set)
    if set != None:
        bone_name = f"{set.name}{div}{bone_name.split(div)[-1]}"
    if bone.drig_function_type == 'IK_BASIC':
        chain = get_bone_chain(object.data.bones[bone_name])
        ik = object.pose.bones[chain[0]].constraints.new('IK')
        ik.chain_count = len(chain)
        add_ik_target_EDIT(object, ik, chain) # Note: Renamed Sets need to be refreshed as the function breaks in the bone menu
        chain[:] = []


classes = [ARMATURE_OT_drig_finalise, 
           ARMATURE_OT_drig_compose,
           ARMATURE_OT_drig_decompose]

def register():
    for cls in classes: bpy.utils.register_class(cls)
def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)