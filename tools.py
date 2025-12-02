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
        #TODO:
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


class ARMATURE_OT_drig_tools_rename_vertex_groups(bpy.types.Operator):
    bl_idname = "armature.drig_tools_rename_vertex_groups"
    bl_label = "Rename Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):
        # Importantly this should also (optionally) rename bones
        # Add a search / text box to pull from

        # name_list = [
        # # old name - new name
        # ['lowerarm_L','forearm.L'],
        # ['lowerarm_R','forearm.R'],
        # ['upperarm_L','upper_arm.L'],
        # ['upperarm_R','upper_arm.R'],]

        # v_groups = bpy.context.active_object.vertex_groups
        # v_groups['name']
        # v_groups['fdcd'].name = 'fff'
        # for n in name_list:
        #     if n[0] in v_groups:
        #         v_groups[n[0]].name = n[1]
        return {'FINISHED'}

# fucking around here.
def render_panel(self, context):

    main = self.layout.column()
    sub1 = main.row()
    sub1.prop(context.scene, 'my_tool', text="", placeholder="Find...")
    sub1.prop(context.scene, 'my_tool', text="", placeholder="Replace...")
    sub1.operator("object.vertex_group_add", icon='ZOOM_ALL', text="")
    sub2 = main.row()
    sub2.prop(context.scene,'sync_bone_names',text="Sync Bones")
    
    

classes = [ARMATURE_OT_drig_tools_apply_pose]

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.my_tool = bpy.props.StringProperty()
    bpy.types.Scene.sync_bone_names = bpy.props.BoolProperty()
    bpy.types.DATA_PT_vertex_groups.append(render_panel)

def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)
    bpy.types.DATA_PT_vertex_groups.remove(render_panel)
    del bpy.types.Scene.sync_bone_names
    del bpy.types.Scene.my_tool

