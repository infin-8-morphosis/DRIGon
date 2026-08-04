
# This has to be done after components are merged

# find_and_connect_at_base() may be useful here...? 
# But if the dupe has the same parent surely in most case we can just flip the suffix

# Functional! Only visual, still needs to symmetrise parenting and properties, 
# But works! 
bone_list = []
for bone in composer.data.edit_bones:
    bone_list.append(bone)

for bone in bone_list:
    if bone.tail.x != 0 or bone.head.x != 0: # Could also check for valid suffix
        dupe = duplicate_bone_EDIT(composer.data, bone.name, son(bone, -1))
        # Uhhhh okay we have to deal with the .001 problem now
        dupe.tail.x = -dupe.tail.x
        dupe.head.x = -dupe.head.x 
        dupe.roll = -dupe.roll
        dupe.use_connect = bone.use_connect
        # Must account for all valid suffixes before release. in a switch/match statement
        dname = list(bone.name)
        print(dname)
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
        