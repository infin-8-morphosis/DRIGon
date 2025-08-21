import bpy, mathutils #type:ignore
from .common import split_name, list_names, copy_armature, get_bone_chain, select_bones
from .common import dnd, div, keep_composer


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

        # Selection: Base
        bpy.ops.armature.drig_make_composer()
        composer = bpy.data.objects[f"{dnd['composer']}{div}{split_name(context.object,1)}"]
        composer.select_set(True) # Selected: Composer | Selection: Composer, Base
        context.view_layer.objects.active = composer
        base = context.object.drig_base
        base.select_set(False) #Deselected: Base | Selection: Composer
        comp_set = composer.data.collections_all[dnd['master_set']]

        if not composer.data.collections_all.get(dnd['base_set']):
            base_set = composer.data.collections.new(dnd['base_set'],parent=comp_set)
        for bone in comp_set.bones_recursive:
            composer.data.collections_all[dnd['base_set']].assign(bone)

        bpy.ops.object.mode_set(mode='EDIT')
        for set in comp_set.children: 
            compose_set(composer, set)
        for bone in base_set.bones:
            if bone.drig_function_type != 'NONE':
                add_drig_function(composer, bone.name)
            # if bone.drig_component_target:
            #     join_drig_component(context, composer, bone.name)
        bpy.ops.object.mode_set(mode='OBJECT')

        composer.drig_fate = 'FINALISE'

        return {'FINISHED'}


# UNTESTED
class ARMATURE_OT_drig_decompose_component(bpy.types.Operator):
    bl_idname = "armature.drig_join_component"
    bl_label = "Join Component"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):
        composer = context.object # Selection: Composer
        base_bone = context.active_pose_bone
        base = composer.drig_base
        component = base_bone.bone.drig_component_target

        bpy.ops.armature.separate()

        return {'FINISHED'}


# # UNTESTED
# class ARMATURE_OT_drig_join_component(bpy.types.Operator):
#     bl_idname = "armature.drig_join_component"
#     bl_label = "Join Component"
#     bl_options = {'REGISTER', 'UNDO'}
    
#     def execute(self,context):
#         composer = context.object # Selection: Composer
#         base_bone = context.active_pose_bone
#         base = composer.drig_base
#         component = base_bone.bone.drig_component_target
#         # Assume the necessary armatures are pre-selected for now...?
#         bpy.ops.object,join()

#         # Important: When decomposing you'll have to reverse these
#         # transforms, apply them, then add them back
#         def save_transform():
#             transform = base_bone.constraints.new('TRANSFORM')
#             transform.mute = True
#             transform.from_min_x = component.location.x
#             transform.from_min_y = component.location.y
#             transform.from_min_z = component.location.z
#             transform.from_min_x_rot = component.rotation_euler.x
#             transform.from_min_y_rot = component.rotation_euler.y
#             transform.from_min_z_rot = component.rotation_euler.z
#             transform.from_min_x_scale = component.scale.x
#             transform.from_min_y_scale = component.scale.y
#             transform.from_min_z_scale = component.scale.z
            
#         bpy.ops.object.mode_set(mode='POSE')
#         save_transform()
#         bpy.ops.object.mode_set(mode='OBJECT')
        
#         return {'FINISHED'}
        

class ARMATURE_OT_drig_finalise(bpy.types.Operator):
    bl_idname = "armature.drig_finalise"
    bl_label = "Finalise Composition"
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


# Copies base, adds new armature, removes all bones from bone groups, except COMPOSITION_SETS.
class ARMATURE_OT_drig_make_composer(bpy.types.Operator):
    bl_idname = "armature.drig_make_composer"
    bl_label = "Make Composer"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):

        def save_transform(object, bone_name, component):
            transform = object.pose.bones[bone_name].constraints.new('TRANSFORM')
            transform.name = f"COMPONENT{div}{component.name}"
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
            print(transform)

            return transform
        
        # Selection: Base
        base = context.object.drig_base 
        composer = copy_armature(base, dnd['composer'], 'FINALISE', keep_composer)
        composer.data = base.data.copy()
        composer.drig_base = base
        cd = composer.data
        bd = base.data
        cd.name = f"{dnd['composer']}{div}{split_name(composer,1)}{div}{split_name(bd,-1)}"

        bpy.data.objects[base.name].select_set(False)
        component_list = []
        for bone in base.data.collections_all[dnd['master_set']].bones_recursive:
            if bone.drig_component_target:
                component_list.append(bone.name)

        for name in component_list:
                bone = base.data.bones[name]
                bpy.data.objects[bone.drig_component_target.name].select_set(False)
                component = bone.drig_component_target.copy()
                component.data = bone.drig_component_target.data.copy()
                context.collection.objects.link(component)
                transform = save_transform(composer, bone.name, component)
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.data.objects[component.name].select_set(True)
                context.view_layer.objects.active = composer
                bpy.ops.object.join()

        for name in component_list:
            # use the transform to join the component base to the component parent bone.
            for each in composer.data.collections_all[dnd['master_set']].bones_recursive:
                if each.head_local == transform: # TODO: Minus component transform so this works outside 0,0,0
                    bpy.ops.object.mode_set(mode='EDIT')
                    composer.data.edit_bones[each.name].parent = composer.data.edit_bones[name]
                    composer.data.edit_bones[each.name].use_connect = True # Not always wanted!
                    bpy.ops.object.mode_set(mode='OBJECT')
                    break
        
        for bone in composer.data.collections_all[dnd['master_set']].bones_recursive:
            bone.name = f"{dnd['base']}{div}{bone.name}"
            bone.use_deform = False

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
    if target.data.edit_bones.get(bone_name):
        targbone = target.data.edit_bones[bone_name]
    else:
        targbone = target.data.edit_bones.new(bone_name)
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
        if base_equiv.parent:
            kept = armature.edit_bones[f"{set.name}{div}{split_name(base_equiv.parent,-1)}"]
        else:
            kept = None
        armature.edit_bones[bone_name].use_connect = connect
        return kept

    def parent_as_equivalent():
        if set.parent.name == dnd['master_set']:
            equiv = None
        else:
            equiv = armature.edit_bones[f"{set.parent.name}{div}{bone_name.split(div)[-1]}"]
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
    if set.drig_trans_target:
        constraint.subtarget = f"{set.drig_trans_target}{div}{bone_name.split(div)[-1]}"
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

# def join_drig_component(context, object, bone_name):
#     bone = object.data.bones[bone_name]
#     base_bone = context.active_pose_bone
#     base = object.drig_base
#     component = base_bone.bone.drig_component_target
#     # Assume the necessary armatures are pre-selected for now...?
#     bpy.ops.object.join()

#     # Important: When decomposing you'll have to reverse these
#     # transforms, apply them, then add them back
        
#     bpy.ops.object.mode_set(mode='POSE')
#     save_transform(component)
#     bpy.ops.object.mode_set(mode='OBJECT')


classes = [ARMATURE_OT_drig_make_composer,
           ARMATURE_OT_drig_finalise, 
           ARMATURE_OT_drig_compose]

def register():
    for cls in classes: bpy.utils.register_class(cls)
def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)