__Drake-Rigger - Notes__

Still gotta make a thing to symmetrise a rig.
    Go through all bones
        Check if the tail-end of the bone is at X 0
        If it isnt, duplicate the bone
        Change the Head and Tail of the bone from + to -, or - to + unless its at 0
        Flip the roll
        Rename it to .L or .R, strip the .001
        Not sure if using ops is better for some of this. Less control.
And a thing to add bones to a vertex groups points in normal orientation
    Can either: Add real bones onto a vertex groups points using vertex parenting
    and some scripting to access the vertex groups points
    Good for front / outer / messy hair that needs fine manipulation
    See DEMON_GeoNodesArmatureHair
Or
    Use geo nodes 'Instance on Points' to instance a bones object on several points
    This would be good for manes and layered hair

Identicality checker:
Get list of bone names from original BASE
Cycle through them and see if original BASE's bones are all:
    In the same position as the decomposed BASE
    Have matching properties
Could generalise this and have it check that RIG is identical to COMPOSER
First we need to actually finalise DECOMPOSER though
Remember, one edit mode!

Tool Idea:
Read textfile and go frame by frame to alter pose based on matching names of pose assets,
the text file would have to be phonetic but... 

Likely ideal is to have a toggle for them.

Alright so transforms arent great... 

Add `assert`s? Perhaps instead of our selection comments?

What we need is some debug tools to test various operations without actually integrating
them into the UI
Maybe also make a folder for various test rigs?
Need better documentation...

What Has Been Done:
    Automatic IK
    Automatically compose set bones
    Create Composer
    Finalise?

What Has Not Been Done:
    Rigify Integration
    Decomposition
    Add sync / rename description to property tooltips

Add tool for mass-renaming Vertex Groups

For decomp: Check what bones have deform on. If yes, check deform on the set.
could completely reverse engineer the set assignments based on what bones are present. Would that even be useful?

Decomp
    Make Decomposer by duping RIG
    Delete everything except BASE
    Reference RIG to ensure the duping process isnt relied on
    Copy drivers to BASE, can you give drivers names using python...?
        I guess use a var name to store the set / bone name. 
        Var name for set, with data store specific bone. If none, assume same bone?


January 2026
----------------------------------------------------------------------------------------------------

I have returned. Decomposition is now sort of a thing. Lots to do but very happy with the 
current work. These files are quite messy...
Probably a goodish ideas to move some things to TODOs in the actual code.


June 2025
----------------------------------------------------------------------------------------------------
TODO: Essential
    Components
        boneproperty to set component
        bpy.ops.object.join() #set active to main object
        in edit mode:
            set componented bone's parent to the (saved) equiv parent of the object.
            option to connect them?
        flip L/R Vertex groups names option (allowing us to mirror limbs) 
        idea: Use an inactive constraint to save the rot loc and scale of a component for decomposing.
            bpy.ops.armature.separate()
    
    Decomposer
        for set in dnd["master_set"].children_recursive:
            for bone in set:
                for constraint in bone.constraint:
                    base.bone[bone.name].select = True
                    constraint.copy_to_selected()
                    base.bone[bone.name].constraint[constraint].name = set.name + constraint.name
                    base.bone[bonename].constraint.enabled = False
                    # also do drivers in some way. cant have multiple on one bone tho
                    base.bone[bone.name].select = False

        for bone in dnd["base_set"]:
            transfer_bone(rig[bone.name], base[bone.name])


TODO: Nice To Have
    Add a Settings tab where you can set what collection IK Controls and such are added to.
    Bone Subdivider function.
        Choose subdiv length
        Run subdiv w/ length
        Assuming the initial bone is the base, go along the chain and rename.
    As bone functions get more specific, probably a good idea to have the UI change based on the
    selected function.
    
Finalise is functional but not suitable.
    ~~Need to make the target have its own armature data. Otherwise BASE gets deleted/edited!~~
    ~~Constraints not copied.~~
    ~~In general things not copied. Parenting, connection. etc.~~
    
Tidied some bugs
Prepped for making the finalise operation

May
----------------------------------------------------------------------------------------------------
    Added basic IK. Still needs a target.
    Prototyped adding target, non-functional currently.

    Formalise the selection process
        deselect the base once the composer is made


2025
----------------------------------------------------------------------------------------------------
    Lets make a debug menu in the UI.
    Try break operators into several functions.
    Rename the internal execute to main??? Very confusing.
    Get non-UI stuff into separate parts of the ui code!
    Try put base and target and stuff into global scope? 

Make the constraints target a different bone group
Alter the constraints target
~~Add deform~~

Add a simple compose button that runs the compose set operator on each set.

Reorg and Composer
----------------------------------------------------------------------------------------------------
    Consider: Use the children[count] of the collections to compose the sets in order,
    which may have the benefit of making the rigs inherently dependency free? (Albeit buggily)
    Oh, how deal with multiple cols with the same prefix? do PREFIX_ANYNAME?
    And less need for messy lists.

Plan
----------------------------------------------------------------------------------------------------
    Basic Composer
        Composer must not exit edit mode before it is done adding or deleting bones.
        We cant copy the base arm to the targets because thatll delete any pose info off 
        of composed bones...
            So we need to transfer them over in ONE edit mode.
            I say for now we create a test armature that runs the process
            And then is joined to the main rig, deletes all the old bones, and strips the renames
            off the new bones
            If we never need to leave edit mode, we can safely do the process to the actual target
            may also be good for the situation of appending sub-armatures, since we cant do that in
            one edit
    Decomposer
        Don't worry about Rigify yet.
        Dupe POSE as BASE.
        Give BASE all the drivers and constraints off FORM and PROX and IK and such.
    Morphs
        Morphs can be made with BASE.
        Dupe POSE as BASE, give POSE locrotscale constraints aimed at BASE.
        Turn off all other constraints?
        Make proportional edits, and hit 'make morph'
        Current MASTER armature is duplicated, dupe is made active. (set all to fake user!)
        Pose is applied.
        MASTER is reactivated. Constraints are cleared, BASE is deleted. All other constraints turned back on.
        Duped Armature is added to a datablock CuProp on the Basis. 
        At some point rename the new morph something appropriate.
    -


Rig Generation
----------------------------------------------------------------------------------------------------
    New Bone Scheme: (Try this!)
        FORM - Deformers. Unconnected. Parent to their POSE/FK equivalent.
        PROX - Proxies parented to their POSE equivalent's PARENT.
        POSE - Main set of bones. Absent from IK.
        IK - Former IK PROX. Connected.
        FK - Former IK POSE. Unconnected. Parented to IK.
        BASE - Used to make morphs/decompose. 

        Able to do away with the many copying constraints? 
        Parent them all to their PROX? 

Code Structure
----------------------------------------------------------------------------------------------------
    Preserving Pose / Animation Data:
        Very important to not clear the armature when regenerating.
        Pose bones don't exist until you exit edit mode,
        so I believe as long as you do it all in edit mode, 
        append the new rig, 
        rename the old bones, 
        remove the .001 off all the new bones,
        and delete the old rig... 
        Then, I believe in pose mode, pose info will be intact as the names never got 'applied'.