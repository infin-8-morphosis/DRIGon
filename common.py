import bpy #type:ignore

keep_composer = True

drig_naming_dict = {
                'divider' : '_',
                'composer' : 'COMPOSER',
				'decomposer': 'DECOMPOSER',
                'base' : 'BASE',
                'target' : 'RIG',
                'armature' : 'ARMATURE',
                'bone' : 'BONE',
                'morph' : 'MORPH',
                'deform' : 'FORM',
                'pose' : 'POSE',
                'proxy' : 'PROX',
                'ik' : 'IK',
                'fk' : 'FK',
				'master_set' : 'COMPOSITION_SETS',
				'base_set' : 'BASE'}
dnd = drig_naming_dict
div = dnd['divider']


def split_name(full_name, part: int):
	split = full_name.name.split(div)
	if part > (len(split)-1): 	return 
	else: 						return split[part]


def list_names(item_list):
    name_list = []
    for item in item_list: name_list.append(item.name)
    return name_list


# Doesnt this assume a single child? How does this process children...?
def get_bone_chain(chain_base,list = []):
	if not chain_base.children:
		list.append(chain_base.name)
		return
	for child in chain_base.children:
		if child.use_connect == True:
			get_bone_chain(child,list)
	list.append(chain_base.name)
	assert list[-1] == chain_base.name, "Chain base not last in list."
	return list


# Returns a copy of an armature with desired name and fate. Adds it to scene optionally.
def copy_armature(old, name, fate: str, link: bool):
	new = old.copy()
	new.name = f"{name}{div}{split_name(old, 1)}"
	new.drig_fate = f"{fate}"
	if link == True: bpy.context.collection.objects.link(new)
	return new

def select_bones(bool: bool, object, blender_mode, name_list = None): # why is blender_mode here...?
	if name_list != None:
		bpy.ops.object.mode_set(mode= blender_mode)
		if blender_mode == 'EDIT': subject = object.data.edit_bones
		elif blender_mode == 'POSE': subject = object.pose.bones
		elif blender_mode == 'OBJECT': subject = object.data.bones
		for name in name_list:
			subject[name].select = bool
			subject[name].select_head = bool
			subject[name].select_tail = bool
	else:
		for each in object.data.edit_bones:
			each.select = bool
			each.select_head = bool
			each.select_tail = bool


classes = []

def register():
    for cls in classes: bpy.utils.register_class(cls)

def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)

