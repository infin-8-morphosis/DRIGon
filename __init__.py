import bpy #type:ignore

from . import propmanager, common, setup
from . import compose, tools#, decompose#, process
from . import ui
# order may be important. ie dont import if havent imported a files dependencies

bl_info = {
    "name": "Drigon",
    "description": "Drake's Rigging Add-On",
    "author": "Drake O. Rex (infin-8-morphosis)",
    "blender": (4, 0, 0),
    "category": "Mesh",
}

classes = []

def register():
    for cls in classes: bpy.utils.register_class(cls)
    propmanager.register()
    common.register()
    setup.register()
    compose.register()
    tools.register()
    #decompose.register()
    #process.register()
    ui.register()
    
def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)
    ui.unregister()
    #process.unregister()
    #decompose.unregister()
    tools.unregister()
    compose.unregister()
    setup.unregister()
    common.unregister()
    propmanager.unregister()
    