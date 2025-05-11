## Drake Rigger

This add-on adds organisational and QoL features to supplement Blender's rigging capabilities.

#### Purpose

Other rigging add-ons like *Rigify* and *Cloudrig* allow you to rig,
without getting into the details of how rigging is done in Blender.
However, they can be too rigid or bloated for particularly strange or simple rigs. 

Drake's Rigging Add-On, or **DRIGon**, is geared towards supplementing manual rigging, rather than bypassing it.
Make simple rigs simpler, or make complex rigs without fighting or altering the add-on.

#### Advice and Considerations

To get the most out of **DRIGon**, you'll need some knowledge of rigging in Blender without add-ons.
In exchange for more freedom, it's on you to set up bones correctly and know how constraints work. 

Have a naming scheme for bones, parent and connect them appropriately, adjust rolls...
In short, be aware that some features usually simplified by other add-ons, 
will need to be used and adjusted.

If you haven't done at least a bit of manual rigging or used another rigging add-on,
try to see if it's a gap in your knowledge before asking if it's an issue with **DRIGon**!

### Usage
-------------

**DRIGon** is accessed from Armature properties, just like *Rigify* and *Cloudrig*,
to allow you to use them in tandem more conveniently.

Press `Initialise` to setup your blendfile for **DRIGon**.

On initialisation, the currently selected armature, prefixed `BASE`, is the **Base**.
It will be composed into one or more **Targets** (Prefixed with `RIG`), 
via a **Composer**, prefixed `COMPOSER`.

Once initialised, you should see a bone group on the **Base** titled `COMPOSITION_SETS`,
with a subgroup titled `BASE`. This is your first **Set**.

If Sets have already been configured, like in the example blendfile,
go ahead and press the `Compose to Target` button, and wait a moment.
The **Target** should have been composed. Go to `Pose Mode` to test it out!
(Can't find it? Look for two boxes at the top of the *DRig* menu, labelled `Base` and `Target`.
Right-click the target box, and press `Jump to Target`. The **Target** should now be selected.

While setting up your own rig, use the example blendfile as a reference.

### Sets
------------

**Sets** are the subgroups of `COMPOSITION_SETS`. 
Each one will be used to compose the bones allocated to it, 
according to the options found in the `Sets` tab of the **DRIGon** menu.
Options include changing the type parenting or transforms of the composed bones. 

These options are used in **DRIGon**'s main function, 'Composing'. 
Composing is similar to generating a rig in *Rigify* or *Cloudrig*, 
(Honestly, the name is different mostly just to prevent confusion.) 
With composing, you get more control over the process.
Sets can be nested in other Sets (Via bone groups) to change the parent of the set, 
if you don't choose to keep parenting intact.

Sets use bone groups, but only via `COMPOSITION_SETS`. 
All other bone groups are yours to use however you please, no need to adjust your setup.

### Structure
-----------------

The **Composer** is used by **DRIGon** in the composing process. 
It is usually deleted after composing, but you can disable that for debugging purposes.
You can also choose whether to finalise the **Target** at all, 
which can be helpful if you're worried about breaking your rig,
and want to make sure it works on the **Composer** first.

If you see the `Initialise` button, but have already initialised the selected armature,
it is likely missing necessary setup pieces.
`Initialise` will attempt to find the missing pieces, or remake them if none are found.

### Technical Details
----------------------

```
common.py           Common functions and names used across the add-on.
compose.py          Operators that compose sets, parts, etc.
decompose.py        Operators for decomposing a rig back into a base.
process.py          Carries out operators.
propmanager.py      All properties related to the add-on.
setup.py            Operators that set up the add-on and its parts.
ui.py               Adds all UI elements.
```
In `common.py`, there is a dictionary named `drig_naming_dict`, that stores all the naming components and affixes.
Feel free to change them, but be aware of potential conflicts caused by untested names.
