import bpy
from .composition import *

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
        
classes = [ARMATURE_OT_drig_compose]

def register():
    for cls in classes: bpy.utils.register_class(cls)
def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)