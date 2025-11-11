import bpy #type:ignore

class ARMATURE_OT_drig_tools_apply_pose(bpy.types.Operator):
    bl_idname = "armature.drig_tools_apply_pose"
    bl_label = "Apply Pose"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):
        # How this should go is that each child of the armature is checked
        # So complex models can be done in one go
        # This could get messy with children of objects though.
        # Currently assumes object is active. Heavily reliant on ops!
        # Also relies on the default armature name. 
        # If multiple, assume 'Armature' is the main one. 
        # Else use the only armature modifier

        #Object
        bpy.ops.object.modifier_copy(modifier="Armature")
        bpy.context.object.modifiers["Armature.001"].show_viewport = False
        bpy.ops.object.modifier_apply(modifier="Armature.001")

        armature = bpy.data.objects["Cube"].modifiers["Armature"].object
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature

        #Armature
        bpy.ops.object.posemode_toggle()
        bpy.ops.pose.armature_apply(selected=False)

        return {'FINISHED'}
	

classes = [ARMATURE_OT_drig_tools_apply_pose]

def register():
    for cls in classes: bpy.utils.register_class(cls)
def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)
