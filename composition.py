import bpy, mathutils
from .common import split_name, list_names, copy_armature, get_bone_chain, select_bones
from .common import dnd, div, br, bl, keep_composer

# This feels unsafe but idk... This grabs all the attributes for EditBones.
property_list = []
for attr in bpy.types.EditBone.bl_rna.properties.items():
    if attr[0] in ['name', 'rna_type', 'collections']: continue
    if attr[0] in ['select', 'select_tail', 'select_head']: continue
    if attr[0] == 'use_connect': continue 
    # Idk if the others are even necessary. This one breaks stuff
    # But previous me had a cryptic if statement about using it...?
    property_list.append(attr[0])
            
# Make a separate one for decomp? Or just get it to check the name of the object?
# Do them separate and see how similar the code is?
# If we move this to its own operator, then have all the identicality checking be in there?
# Since finalise makes sense to be when the old BASE and the new BASE are compared.
# When doing that dont forget to save the old BASE before it gets overwritten lol
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


def map_bone_settings(receiver, sender, final):
        if final: #What is this...
            pass
            # receiver.use_connect = sender.use_connect
        # receiver.head = sender.head
        # receiver.tail = sender.tail
        # receiver.matrix = sender.matrix
        # What are these...?

        for prop in property_list:
            if sender.is_property_readonly(prop): continue
            setattr(receiver, prop, getattr(sender, prop))

        # receiver.parent = sender.parent
        # receiver.inherit_scale = sender.inherit_scale
        # receiver.use_deform = sender.use_deform
        # receiver.bbone_segments = sender.bbone_segments
        # receiver.bbone_rollout = sender.bbone_rollout
        # receiver.bbone_rollin = sender.bbone_rollin
        # receiver.bbone_easein = sender.bbone_easein
        # receiver.bbone_easeout = sender.bbone_easeout
        # receiver.bbone_x = sender.bbone_x
        # receiver.bbone_z = sender.bbone_z
        # receiver.bbone_handle_type_start = sender.bbone_handle_type_start
        # receiver.bbone_custom_handle_start = sender.bbone_custom_handle_start
        # receiver.bbone_handle_type_end = sender.bbone_handle_type_end
        # receiver.bbone_custom_handle_end = sender.bbone_custom_handle_end

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

def split_bone_recursive_EDIT(object, bone, amount: int, start = True, count = 0):
    if amount <= 0: return "Don't."
    bpy.ops.armature.subdivide()             
    bone.select = False
    print(context.selected_bones[0])
    object.data.edit_bones.active = context.selected_bones[0]
    count += 1
    if amount == count:
        return
    else:
        bone = object.data.edit_bones.active
        split_bone_recursive_EDIT(object, bone, amount, False, count)

classes = [ARMATURE_OT_drig_finalise]

def register():
    for cls in classes: bpy.utils.register_class(cls)
def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)