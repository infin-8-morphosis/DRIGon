Other Ideas
----------------------------------------------------------------------------------------------------
    Character selector
        Have a CuProp on the armature data with the object (and its children) you want to show 
        Hide all other objects parented to the rig object.
```
    Terminology clarifier
        ie what is basis, template, morph, etc.
```
    Better armature symmetriser
```
    naturalistic breathing scale function for driver
        sin( (pi/2) * (4/5) * cos(frame/20) / 4 ) + 1
```


Sets
----------------------------------------------------------------------------------------------------
    Add buttons to add more sets

    Advanced Feature:
    Composer panel, add things you want to happen and the order they happen in, like composing to
    subtargets, adding sets, etc.
    Armature objects beginning with COMPONENT_ can be accessed like rigify types, will be
    duped and joined to the bone theyre set to (after being parented to said bone)
    Have property on said bone that will alter the components bone names,
    so component left, right, hind, fore
    Possible to integrate asset libraries into that?




    Drake IK but automated
        Have a N panel option to turn IK rotation on/off

    Rev would like to automatically check deform on raw_copy!

    Automatic rig symmetriser
    Automatic multi-rig merger / duplicator

    Duplicate genrig bones with PROX
    Duplicate genrig bones with POSE
    If deform is checked
        Duplicate genrig bones with FORM
    Disconnect all FORM, and parent them to their POSE.
    Disconnect all NON-IK PROX bones and parent them to themselves's PARENT.
        I think that will prevent looping...?

    Copy BASE bone drivers to corresponding PROX bones.
        Retarget drivers to genrig bones.

    Apply current pose
        Get name of current pose. if none, generate normally
        Find armature ending with the pose's name
        make blank armature with that pose, append it to the template.

    Rename genrig bones with BASE_ prefix (Delete them once everything is transferred.)
        (Or keep in their own collection, if wanted.)

    Can set start/end handle of B-Bones, then don't need to have FORM connected, or POSE.

Rig Setup
----------------------------------------------------------------------------------------------------
        Seperate custom properties between edit and pose mode!
        Remember, you can't save anything in edit mode. Names only.
            Edit CuProps:
                FORM/POSE/PROX_Parent
                FORM/POSE/PROX_Scale_Inheritance (BBones)
            Pose CuProps:
                Component

    Use name of Constraint to change target.
        POSE_Contraint_PROX - Constraint will be put on POSE, and its targets are PROX.

    DIY Components / Appendable rigs
        Make a rig with just the component
        Append each to a collection of empties, each vert in a vert group, each bone with certain name, etc.

Reverse Rigger
----------------------------------------------------------------------------------------------------
    For Rigify:
        *No can do. ORG is not an exact replica.*
            Select all ORG bones, and all raw_copy bones.
            Separate them from the rig.
            Delete all the bones off the metarig. (Have a property for which object is the basis)
            Join the separated rig to the metarig.
        Best compromise is to make your own, actually-faithful ORG collection.
    
    For Drake:
        POSE is the 'main set'. Duplicate it, name it BASIS.
        Search for FORM equivalent:
            If equivalent, set BASIS to Deform, copy its B-Bone settings into CuProps.
            If not, set BASIS to no deform, just in case.
        Get all drivers off PROX and put them on their BASIS bone.
        Tricky but, check for constraints on FORM and PROX:
            If constraints, rename them (PROX_/FORM_) and copy them to BASIS.
            If none, skip.

UI
----------------------------------------------------------------------------------------------------

Morphs
----------------------------------------------------------------------------------------------------