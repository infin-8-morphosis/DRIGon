import bpy #type:ignore
from .common import split_name, list_names, copy_armature, get_bone_chain
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


        def add_composer():
            bpy.ops.armature.drig_make_composer()
            composer = bpy.data.objects[f"{dnd['composer']}{div}{split_name(context.object,1)}"]
            composer.select_set(True)
            context.view_layer.objects.active = composer
            return composer

        composer = add_composer()
        comp_sets = composer.data.collections_all[dnd['master_set']]
        base_set = composer.data.collections_all[dnd['base_set']]

        bpy.ops.object.mode_set(mode='EDIT')
        for set in comp_sets.children: 
            compose_set(composer, set)
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


# Copies base, adds new armature, removes all bones from bone groups, except COMPOSITION_SETS.
class ARMATURE_OT_drig_make_composer(bpy.types.Operator):
    bl_idname = "armature.drig_make_composer"
    bl_label = "Make Composer"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):
        
        base = context.object.drig_base
        composer = copy_armature(base, dnd['composer'], 'FINALISE', keep_composer)
        composer.data = base.data.copy()
        cd = composer.data
        bd = base.data
        cd.name = f"{dnd['armature']}{div}{split_name(composer,1)}{div}{split_name(bd,-1)}"

        # Er... Why? Don't we need bone groups preserved?

        # for collection in composer.data.collections_all:
        #     for bone in collection.bones: collection.unassign(bone)
        for bone in composer.pose.bones: 
            bone.name = f"{dnd['base']}{div}{bone.name}"

        return {'FINISHED'}


def duplicate_bone_EDIT(armature, bone_name, set):
    copy_name = f"{set.name}{div}{bone_name.split(div)[-1]}"
    copy = armature.edit_bones.new(copy_name)
    copy.name.removesuffix('.001')
    copy.head = armature.edit_bones[bone_name].head
    copy.tail = armature.edit_bones[bone_name].tail
    copy.matrix = armature.edit_bones[bone_name].matrix
    return copy

def determine_parent_EDIT(armature, bone_name, set):
    if set.parent.name == dnd['master_set']:
        equiv = None
    else:
        equiv = armature.edit_bones[f"{set.parent.name}{div}{bone_name.split(div)[-1]}"]
    if armature.edit_bones[bone_name].parent != None:
        kept = armature.edit_bones[f"{set.name}{div}{split_name(equiv.parent,-1)}"]
    else:
        kept = None
    
    method = set.drig_parent_method
    if method ==   'KEEP':              return kept
    elif method == 'EQUIV':             return equiv
    elif method == 'EQUIV_PARENT':      return equiv.parent
    elif method == 'EQUIV_CHAIN':
        if not equiv.use_connect:       return equiv
        if equiv.use_connect:           return kept

def add_trans_constraints(object, bone_name, set):
    type = f'COPY_{set.drig_trans_type}'
    constraint = object.pose.bones[f"{bone_name}"].constraints.new(type)
    constraint.target = object
    if set.drig_trans_target:
        constraint.subtarget = f"{set.drig_trans_target}{div}{bone_name.split(div)[-1]}"
    else:
        constraint.subtarget = f"{set.parent.name}{div}{bone_name.split(div)[-1]}"
    #alter constraint settings here

#    TO-DO
#   Works on its own! Needs integration / add more settings
def add_ik_basic(object, bone_name, set):
    if object.bones[bone_name].drig_function_type == 'IK_BASIC':
        chain = get_bone_chain(object.bones[bone_name])
        ik = object.pose.bones[chain[0].name].constraints.new('IK')
        ik.chain_length = len(chain)


classes = [ARMATURE_OT_drig_make_composer, ARMATURE_OT_drig_compose]

def register():
    for cls in classes: bpy.utils.register_class(cls)
def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)