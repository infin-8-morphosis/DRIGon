import bpy
from .common import split_object_name as son, copy_armature
from .common import dnd, div


# Checks every armature for correct target / base properties, sets fates and 
# checks for rigify.
class ARMATURE_OT_drig_initialise(bpy.types.Operator):
    bl_idname = "armature.drig_initialise"
    bl_label = "Initialise"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):


        def main():
            if not (selection := context.scene.drig_morph_select):
                selection = None
            for object in bpy.data.objects:
                if object.type != 'ARMATURE': continue
                elif object.drig_target_main and object.drig_base: continue
                else:
                    if find_stray_assignments(object): print("Stray Found!")
                    else:
                        rigify_check = check_for_rigify(object.data)
                        object.drig_fate = determine_fate(rigify_check,object)
            

        def determine_fate(rigify_check, subject):

            base = subject.drig_base
            target = subject.drig_target_main
            data = subject.data
            
            if rigify_check == False:
                if base and not target:             return 'NEW_TARGET_COMPOSE'
                else:                               return 'PREPARE_BASE'
            else:
                if data.get('rig_id'):              return 'INCOMPATIBLE' 
                elif data.get('rigify_target_rig'): return 'PREPARE_RIGIFY_COMPATIBILITY'

                elif base and not target:           return 'NEW_TARGET_COMPOSE'
                else:                               return 'PREPARE_BASE'


        def find_stray_assignments(suspect):

            if son(suspect,0) not in dnd.values():
                return False

            for object in bpy.data.objects:

                if object.type != 'ARMATURE': continue
                if son(object,0) not in dnd.values(): continue
                if son(suspect,0) == son(object,0): continue

                if object.drig_base == suspect.drig_base:
                    suspect.drig_target_main = object
                    return True
                elif object.drig_target_main == suspect.drig_target_main:
                    suspect.drig_base = object
                    return True

                if son(suspect,1) == son(object,1):
                    if son(object,0) == dnd['target']:
                        suspect.drig_target_main = object
                        object.drig_base = suspect
                        return True
                    elif son(object,0) == dnd['base']:
                        object.drig_target_main = suspect
                        suspect.drig_base = object
                        return True

            return False

        #How to make this shorter...?
        def check_for_rigify(armature):
            try:
                if (
                    bpy.types.Armature.rigify_target_rig or 
                    armature.get("rig_id") or 
                    armature.get('rigify_target_rig')
                    ):
                    return True
            except:
                return False


        main()
        return {'FINISHED'}



# Adjusts properties and names, adds COMPOSITION_SETS. Assigns all current 
# bones to BASE set.
class ARMATURE_OT_drig_prepare_base(bpy.types.Operator):
    bl_idname = "armature.drig_prepare_base"
    bl_label = "Prepare Base"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):
        
        base = context.object
        base.drig_base = base
        base.name = f"{dnd['base']}{div}{base.name}"
        base.data.name = f"{dnd['morph']}{div}{base.name.split(div,1)[1]}{div}MASTER"
        base.drig_fate = 'NEW_TARGET_COMPOSE'

        comp_set = base.data.collections.new(dnd['master_set'])
        base.data.collections.new('SET',parent=comp_set)

        bpy.ops.object.mode_set(mode='EDIT')
        for bone in base.data.edit_bones:
            base.data.collections_all['SET'].assign(bone)
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}



# Copies base and adds itself to the scene, adjusts properties.
class ARMATURE_OT_drig_make_target(bpy.types.Operator):
    bl_idname = "armature.drig_make_target"
    bl_label = "Make New Target"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):

        
        base = context.object
        target = copy_armature(base, dnd['target'], 'DECOMPOSE')
        context.collection.objects.link(target)
        target.data.name = f"{dnd['armature']}{div}{son(base,1)}{div}{son(base.data,-1)}"
        base.drig_target_main = target
        base.drig_fate = 'FINALISE'
        target.drig_target_main = target
        if son(context.object,0) == 'COMPOSER':
            target.drig_base = context.object.drig_base
        else:
            target.drig_base = base

        return {'FINISHED'}



classes = [ARMATURE_OT_drig_initialise,
           ARMATURE_OT_drig_prepare_base,
           ARMATURE_OT_drig_make_target]

def register():
    for cls in classes: bpy.utils.register_class(cls)
def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)