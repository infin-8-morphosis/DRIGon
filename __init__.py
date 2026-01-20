import bpy #type:ignore

from . import propmanager, common, setup
from . import composition, tools
from . import op_compose, op_decompose
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
    composition.register()
    tools.register()
    op_compose.register()
    op_decompose.register()
    ui.register()
    
def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)
    ui.unregister()
    op_decompose.unregister()
    op_compose.unregister()
    tools.unregister()
    composition.unregister()
    setup.unregister()
    common.unregister()
    propmanager.unregister()
    