__Drake-Rigger - Notes__

May
----------------------------------------------------------------------------------------------------
    Added basic IK. Still needs a target.
    Prototyped adding target, non-functional currently.


2025
----------------------------------------------------------------------------------------------------
    Lets make a debug menu in the UI.
    Try break operators into several functions.
    Rename the internal execute to main??? Very confusing.
    Get non-UI stuff into separate parts of the ui code!
    Try put base and target and stuff into global scope? 

Make the constraints target a different bone group
Alter the constraints target
Add deform

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