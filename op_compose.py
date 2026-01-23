import bpy
from .composition import *
from .common import copy_armature, keep_composer


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
            # I really feel like this should be tidied...


        base = context.object.drig_base # Selection: Base
        composer = copy_armature(base, dnd['composer'], 'FINALISE')
        if keep_composer: context.collection.objects.link(composer)
        composer.drig_base = base
        sn = split_name
        composer.data.name = f"{dnd['composer']}{div}{sn(composer,1)}{div}{sn(base.data,-1)}"

        bpy.data.objects[base.name].select_set(False) #Deselected: Base | Selection: None

        merge_components(base, composer)

        collections = composer.data.collections_all

        for bone in collections[dnd['master_set']].bones_recursive:
            bone.name = f"{dnd['base']}{div}{bone.name}"
            bone.use_deform = False

        composer.select_set(True) # Selected: Composer | Selection: Composer
        context.view_layer.objects.active = composer

        comp_set = collections[dnd['master_set']]

        if not collections.get(dnd['base_set']):
            base_set = composer.data.collections.new(dnd['base_set'],parent=comp_set)
        for bone in comp_set.bones_recursive:
            base_set.assign(bone)
        
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



classes = [ARMATURE_OT_drig_compose]

def register():
    for cls in classes: bpy.utils.register_class(cls)
def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)