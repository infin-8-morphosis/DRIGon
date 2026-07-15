# Took a screenshot of this fixedish but it seemingly crashed blender
# We seemed to have put this into blenders script reader thing
# Tedious but yes. It does crash. badly. Memory leak? Infinite loop?
# Didnt actually execute the function though?

def duplicate_bone_EDIT(armature, bone_name, set):

    copy_name = f"{set}{div}{bone_name.split(div)[-1]}"
    copy = armature.edit_bones.new(copy_name)
    # TODO: lmao it doesnt work with the numbers? How has this not caused problems?
    # if bone_name.split('.')[-1] == '.001':
    #     copy.name.removesuffix('.002')
    # else:
    copy.name.removesuffix('.001')
    map_bone_settings(copy, armature.edit_bones[bone_name], False)
    return copy

# This has to be done after components are merged

# !!! I see the problem. You need to get the list of bones. 
# Here youre probably infinitely editing the edit bones names and it never finishes.

for bone in composer.data.edit_bones:
    if bone.tail.x != 0 or bone.head != 0: # Could also check for valid suffix
        dupe = duplicate_bone_EDIT(composer.data, bone.name, split_name(bone, -1))
        # Uhhhh okay we have to deal with the .001 problem now
        dupe.tail.x = -dupe.tail.x
        dupe.head.x = -dupe.tail.x 
        dupe.roll = -dupe.roll
        # Must account for all valid suffixes before release. in a switch/match statement
        dname = list(dupe.name)
        if bone.name.endswith('.L'):
            dname[-1] = 'R'
            dupe.name = "".join(dname)
        elif bone.name.endswith('.R'):
            dname[-1] = 'L'
            dupe.name = "".join(dname)
        else:
            if bone.tail.x < 0 or bone.head.x < 0:
                bone.name += '.L'
                dupe.name += '.R'
            else:
                bone.name += '.R'
                dupe.name += '.L'
        