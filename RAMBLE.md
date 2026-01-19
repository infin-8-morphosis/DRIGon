Notes
----------------------------------------------------------------------------------------------------
    I think we could get away with applying the rig... yes, we'll have to redo UV's every
    so often but as long as we have a file on hand for the layout we can make things
    mostly consistent. Losing scaling or accidentally messing up models is worse...

Code Snippets
----------------------------------------------------------------------------------------------------
```
    Ask if block exists / get block if unsure block exists
        bpy.context.scene.objects.get("RIG_Armature")
```
    Checks deform on all bones with FORM_ in name, unchecks it on everything else
        for bone in bpy.context.object.data.edit_bones:
            if 'FORM_' in bone.name:
                bone.use_deform = True
            else:
                bone.use_deform = False
        -
```
    Template for adding functions to drivers. No more need to fit into that tiny textbox!
        def custom_driver(x,y,z):
            return x y x
        bpy.app.driver_namespace["my_custom_driver"] = custom_driver
```
    Make dictionary {'man' : 2, etc} in CuProp and access it (only string, int, float, etc.)
        bpy.context.object["Property"]['man'] 
            2
```
    Accessing drivers / determining driver location:
        C.object.animation_data.drivers[0].data_path
        'pose.bones["Bone"].location'

