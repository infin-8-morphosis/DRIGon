import bpy #type:ignore
from bpy.types import (Panel, Operator, Armature) #type:ignore
from .common import split_name, dnd, div

class BONE_PT_drig_ui_bones(bpy.types.Panel):
    bl_label = "Drigon"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        object = context.object
        armature = object.data
        bone = context.active_bone

        main = self.layout.row()
        func_area = main.column()
        comp_area = main.column()

        func_area.label(text="Function", icon = "INFO")
        func_area.prop(bone,'drig_function_type', text="", placeholder="Type")
        func_area.prop_search(bone, 'drig_function_set', armature, "collections_all", text="")

        comp_area.label(text="Component", icon = "INFO")
        comp_area.prop(bone,'drig_component_target', text="", placeholder="Target")
        comp_area.prop_search(bone, 'drig_component_set', armature, "collections_all", text="")

class DATA_PT_drig_ui_main(bpy.types.Panel):
    bl_label = "Drigon"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.object.type == 'ARMATURE'

    def draw(self, context):

        object = context.object
        armature = object.data

        def determine_operations():
            fate = context.object.drig_fate
            if not context.object.drig_target_main or not context.object.drig_base:
                if      fate == 'PREPARE_BASE':                 main = 'armature.drig_prepare_base'
                elif    fate == 'PREPARE_RIGIFY_COMPATIBILITY': main = 'mesh.primitive_cube_add'
                elif    fate == 'NEW_TARGET_COMPOSE':           main = 'armature.drig_compose'
                else:                                           main = 'armature.drig_initialise'
            elif fate == 'COMPOSE':                             main = 'armature.drig_compose'
            elif fate == 'DECOMPOSE' or fate == 'INCOMPATIBLE': main = 'mesh.primitive_cube_add'
            else:                                               main = 'armature.drig_initialise'
            operations.operator(main)
            operations.operator('armature.drig_compose')
            operations.operator('armature.drig_make_target')
            operations.operator('armature.drig_make_composer')
        
        def determine_alerts():
            if not object.get('drig_rigify_compatibility') and armature.get("rig_id"):
                alerts.box().label(
                    text="No Rigify compatibility. Compose via the metarig!", 
                    icon = "INFO")
                operations.enabled = False
        
        main = self.layout.column()

        alerts = main.column()
        determine_alerts()
        operations = main.column()
        determine_operations()

        if object.get('drig_base'):

            titles = main.row()
            subjects = main.row()

            titles.label(text="Base")
            titles.label(text="Target")

            base = subjects.column()
            target = subjects.column()
            
            base.prop(object,'drig_base', text="", placeholder="Base")
            target.prop(object,'drig_target_main', text="", placeholder="Not Composed")

            if object == object.drig_base:
                base.enabled = False
            if object == object.drig_target_main:
                target.enabled = False

class DATA_PT_drig_ui_rig_structure(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_label = "Rig Structure"
    bl_parent_id = 'DATA_PT_drig_ui_main'
    
    @classmethod
    def poll(cls, context):
        return context.object.get('drig_base')

    def draw(self, context):

        object = context.object
        armature = object.data
        set_master = armature.collections_all['COMPOSITION_SETS']

        def draw_set(set,child_box=None):
            if child_box != None:
                test = child_box.row()
                test.separator()
                test.separator()
                box = test.box().split(factor=0.25)
            else:
                test = structure.box()
                box = test.split(factor=0.2)

            info = box.column()
            settings = box.column()

            parent = settings.row()
            settings.separator(type='LINE')
            trans = settings.row()

            info.label(text= set.name)
            info.separator(type='LINE')
            info.prop(set,'drig_set_deform',text="Deform")
            
            parent.label(text='', icon='CON_CHILDOF')
            parent.prop(set,'drig_parent_method', text="", placeholder="Parenting Method")
            
            trans.label(text='', icon='DRIVER_TRANSFORM')
            trans.prop_search(set, 'drig_trans_target', armature, "collections_all", text="")
            trans.prop(set,'drig_trans_type', text="", placeholder="")

            if set.children:
                for child_set in set.children: draw_set(child_set,child_box=structure)
            if child_box != None:
                pass
            else:
                structure.separator(type='LINE')
        
        structure = self.layout.column()
        for set in set_master.children:
            draw_set(set)


class DATA_PT_drig_ui_morphs(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_label = "Morphs"
    bl_parent_id = 'DATA_PT_drig_ui_main'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        object = context.object.data
        return split_name(object,0) == dnd['morph']

    def draw(self, context):

        object = context.object


        layout = self.layout

        layout.separator()
        morph_list = layout.box()
        layout.separator()
        search = layout.column()
        edit = layout.row()
        layout.separator()

        search_picker = search.prop(context.scene, 'drig_morph_select', text="", placeholder="Pick a Morph to Add or Edit" )
        search_alert = search.column()

        edit.operator("mesh.primitive_cube_add", text="Add Morph")
        edit.operator("mesh.primitive_cube_add", text="Clear Morph")
        edit.operator("mesh.primitive_cube_add", text="Delete Morph")

        name = split_name(object.data,-1)
        morph_list.prop(object.data,'name',text=f"{name.capitalize()}", icon="ARMATURE_DATA")

        for armature in bpy.data.armatures:
            if armature == object.data:
                continue
            split = armature.name.split(div)
            if split[0] != dnd['morph']:
                continue
            if split[1] != split_name(object.data.name,1):
                continue
            else:
                name = split[-1]
                morph_list.prop(armature,'name',text=f"{name.capitalize()}", icon="ARMATURE_DATA")

        if context.scene.drig_morph_select == object.data:
            search_alert.box().label(text="You can't edit the Master Morph!", icon = "INFO")
            edit.enabled = False


class DATA_PT_drig_ui_info(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_label = "Info"
    bl_parent_id = 'DATA_PT_drig_ui_main'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.object.get('drig_base')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        object = context.object
        armature = context.object.data

        column = layout.column()


classes = [BONE_PT_drig_ui_bones,
           DATA_PT_drig_ui_main,
           DATA_PT_drig_ui_rig_structure,
           DATA_PT_drig_ui_morphs, 
           DATA_PT_drig_ui_info]

def register():
    for cls in classes: bpy.utils.register_class(cls)
def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)
