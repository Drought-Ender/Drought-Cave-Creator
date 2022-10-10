# Drought Ender's Cave Creator 

## Presets & Preset Settings

### What is a preset folder?

#### What does it do?

In the repository, you have have noted a folder named *presets* containing a signular preset titled *pikmin2*, this folder is designed to allow you to create custom enemy and treasure groups for a hack without having to re-write any code within cave creator beforehand.

#### What does it contain?

##### teki.json
this is a .json file containing every enemy, it is formated like this:
```
{internal name (string) : 
{"common" : common name (string), 
"id" : piklopedia id (int), 
"use" : show teki (bool) }
}
```
##### item.json
this is a .json file containing every treasure, it is formated like this:
```
{internal name (string) : common name (string) }
```

##### preset.ini
this is a file containing the locations of items in use with the editors, you do not need to worry about it.

##### tekiIcons
this is a folder containing .pngs of each enemy listed in *teki.json*

##### itemIcons
this is a folder containing .pngs of each treasure listed in *item.json*

### Creating a new preset
1. Copy the *pikmin2* preset and rename it to whatever you'd like
2. Add any custom treasures' names into *item.json*
3. Add any custom enemies' names into *teki.json*
4. (optional) update *tekiIcons*
5. (optional) update *itemIcons*

you're now ready to use the preset for whatever mod you'd like

### Preset Settings

#### Where is it?
Preset settings can be found in the *options* menu, and has it's own button and text box for it.

##### Note:
Attempting to load or edit the presets of a non-existing directory will throw a warning and disallow you from doing so, make sure it's spelt right and using correct capitalization.

#### Setting up

After opening the presets menu, there will be 5 buttons, excluding **Save Preset Settings**. These buttons are:
- Open units txts from folder
- Open caves from folder
- Open units arc from folder
- Open lighting from folder
- Set all from root folder

The text boxes below them contain the locations that will be opened from when required during usage from the editors. 
To set it up properly, simply click the **Set all from Root folder** button, and open the root of the hack's folder, then press **Save Preset Settings** and close the tab - your preset it is ready to be used for modding, have fun!
##### Note:
If you're using a file framework that restructures the locations and names of the folders, the **Set all from Root folder** button will fail to find the folders for each setting - if that is the case, you will have to path to the folders containing the items for each setting by hand.

## Cave Editor

### Accessing Caves

#### Open Cave
**Open Cave** will route you to you're preset's caves folder, where you can select a cave file to load into the editor with.

#### New Cave
**New Cave** will jump you straight into the editor with a completely blank cave, where you can save your cave to a location immediantly

#### Load Backup
**Load Backup** will route you to the _Backups_ folder, in which backed-up _.pickle_ files will be stored, clicking on one of them will load the backed-up cave.

### Saving Current Cave

#### Save As

To save the current cave to a new location, select **File -> Save As** or use **Ctrl + Shift + S**, this will open a dialoge to save the file the a desired location.

#### Save

To overwrite the cave that is being worked on, select **File -> Save** or use **Ctrl + S**, this will overwrite the file that is saved over, so be careful.

#### Backup

To backup to the backups folder, selected **File -> Backup** or use **Ctrl + B**, this will create a *.pickle* backup that can be easily loaded.
##### Note:
pickling is not a secure method of storage, do not accept *.pickle* files from people you do not trust.

### Reading the GUI

#### Floors
In the top center of the cave editor is an enumerated bar of the floors within the cave. Left of that bar is two buttons, one that says *Add Floor* and one that says *Remove Floor*, their functions are self explanatory

##### Note:
Remove a floor by accident? Do not fear, the floor itself is not deleated, clicking *Add Floor* will return the floor back before it was deleated.

#### Floorinfo

The first section of the floor is denoted as *Floorinfo*, and it looks like this:

![Floorinfo Example](https://github.com/Drought-Ender/Drought-Cave-Creator/blob/main/Assets/Floorinfo%20Example.png)

- Units File: A .txt containing units instructions
- Lighting File: A .ini file containing lighting instuctions
- Skybox: The name of the VRBOX in use
- Spawn Collision Plane: Tells the game to spawn an invisable floor of collision if checked, used in some cave themes
- Spawn Geyser: Tells the game to spawn an exit geyser on this sublevel
- Clogged Hole: Tells the game whether it should put a clog on the hole this sublevel or not
- Teki Number: Total amount of enemies the game will spawn on this floor
- Item Number: Total amount of items the game will spawn on this floor (not including items in enemies)
- Gate Number: Total amount of gates the game will spawn on this floor
- Room Number: Total amount of rooms the game will spawn when creating the floor
- Corridor Chance: Chance of a corridor being selected to spawn instead of a room, values above 0.20 are disencouraged
- Dead End %: Chance of a hallway spawning a dead end instead
- Echo Type: The type of echo used within the sublevel, soil is the strongest, toy is the weakest
- Music Type: The type of music used within the sublevel, *Normal* plays the regular music defined in *Totaka*'s folder, *Boss* silences the floor until a boss encounter, *Rest* plays rest floor music.
- Wraith Timer: Time until the Waterwraith spawns if it is placed in a level and not used on the final floor.
- Spawn Seesaws: Tells the game to randomly place 2 conected seesaws throughout the level
- Use Capinfo: Toggles the Capinfo box

#### TekiInfo
The second section of the floor is denoted as *Tekinfo*, and it looks like this:

![TekiInfo Example](https://github.com/Drought-Ender/Drought-Cave-Creator/blob/main/Assets/Teki%20Example.png)

##### Note:
In order to save space, these are not labeled within the cave creator

- Teki Name: A dropdown menu featuring every enemy, can be changed to a text menu in settings, or changed to a custom preset.
- Held Item: A dropdown meanu featuring every treasure can be changed to a text menu in settings, or changed to a custom preset.
- Fall Type: A dropdown menu for every fall activation, *None* means it will not fall.
- Spawn Count: The leftmost Number Slider, sets how many teki the game will spawn
- Weight: The rightmost Number Slider, sets how many filler enemies the game will spawn
- Spawn Group: The type of location the game will spawn the enemy at, *Unknown* will not spawn one. Can be changed to internal names in settings
- Add Teki: Adds another enemy to TekiInfo
- Remove Teki: Removes the bottom-most enemy


#### ItemInfo:
The third section of the floor is *Iteminfo*, it looks like this: ![Iteminfo Example](https://github.com/Drought-Ender/Drought-Cave-Creator/blob/main/Assets/Item%20Example.png)

##### Note:
In order to save space, these are not labeled within the cave creator

- Item:  A dropdown meanu featuring every treasure can be changed to a text menu in settings, or changed to a custom preset.
- Count: The number of this item to be spawned, only change this for challenge mode levels.
- Weight: Not shown in the above photo, and must be enabled in settings; this is the amount of filler treasures to spawn, not recomended.
- Add Item: Adds another treasure to ItemInfo
- Remove Item: Removes the bottom-most treasure

#### GateInfo:
The forth section of the floor in *GateInfo*, it looks like this:
![Gateinfo Example](https://github.com/Drought-Ender/Drought-Cave-Creator/blob/main/Assets/Gate%20Example.png)
##### Note:
In order to save space, these are not labeled within the cave creator

- Name: Not shown in the above photo, a text bar with the name of the gate, this does not effect the cave and is not recomended.
- Life: The amount of health the gate has, a pikmin deals 20 damage per second.
- Weight: ***THIS IS NOT THE SPAWN NUMBER*** - This is the weighing of the gate, the amount of gates to spawn is located in floorinfo.
- Add Gate: Adds another gate to gateinfo
- Remove Gate: Removes the bottom-most gate

#### CapInfo:
The fifth and final section of the floor is CapInfo, it looks like this 
![Gateinfo Example](https://github.com/Drought-Ender/Drought-Cave-Creator/blob/main/Assets/Cap%20Example.png)

##### Note:
In order to save space, these are not labeled within the cave creator

##### Note:
You may notice that the capinfo section is missing, that is because it has been disabled in floorinfo and can be re-enabled at any time.

- Teki Name: A dropdown menu featuring every enemy, can be changed to a text menu in settings, or changed to a custom preset.
- Held Treasure: A dropdown meanu featuring every treasure can be changed to a text menu in settings, or changed to a custom preset.
- Fall Type: A dropdown menu for every fall activation, *None* means it will not fall.
- Spawn Num: The leftmost Number Slider, sets how many teki the game will spawn
- Weight: The rightmost Number Slider, sets how many filler enemies the game will spawn
- Captype: If disabled, this will make 2 of an enemy spawn in the cap instead of one, useful for things like anode beetles, but not generally recomended.
- Add Cap Teki: Adds another cap enemy to CapInfo
- Remove Cap Teki: Removes the bottom-most enemy

## Units Editor
This feature is planned, but has not been implemented yet

## Lighting Editor
Instructions comming soon

## Unit Layout Editor
This feature is planned, but has not been implemented yet, this will not be added on release

