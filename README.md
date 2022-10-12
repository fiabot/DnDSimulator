# DnDSimulator

DnD simulator with game-playing agents for automatic play testing. This file outlines the DnD simulator and how to use. For a more in depth explanation of agents and results, see PDF provided.  

## Simulation 
This is a prototype version of a DnD encounter simulator. It currently allows creatures to complete one movement and one action (in that order) per turn. The movement available is determined by a speed, which determine how many spaces a creature can move in a turn. The way I implemented it, a space is worth 10 ft. The actions available are either an attack or a spell. The game runs until all of one party is immobile (cannot move or act) or a turn limit is reached. The turn limit was determined by the thrown food theory, which is the estimated amount of time it would take for a party to be fed up with an encounter and decide to throw food at the GM. 

Simplications were made to the similation using the following principles: 

* The game environment (represenation of creatures and maps) can be condensed such that the fewest amount of information about it can be stored 

* Players and monsters should select from the fewest number of choices possible, without limiting their power 

* Rules and mechanics can be condensed to what would happen most of the time, even if there are some outlier cases 

* Game content available to the simulation, such as special features or spells, can be limited to the most frequent instances or categories 

* This simulation is limited to players at level 1 and monsters at challenge level 1 

* For mechanics (particularly spells) that have large action spaces, the simulation can use a random sample of those spaces rather than the complete action space 

* Rules and mechanics that are not predominantly focused on combat are not considered in this simulation 



### Grid 
A grid (or map) is defined by a width and a height. Pieces can be added to the grid, as long as they have a position attribute. The grid class allows you to do things such as find the distance between two points, get the pieces that are in a range of position, or get the enemy closest to a creature. 

### Creature 
A creature are defined through the following properties 

ac = numerical armor class 

hp = max hit points either as value or dice roll, depending on rolled value 

name = name of creature 

team = what side creatures fights for, decides who is an enemy or friend 

action = available actions as a list 

speed = amount creatures is able to move in grid units 

features = a feaature manager with any special features added 

modifers = skill and saving throw mods, along with intative  

immunities = damage types the character cannot take damage from

resistences = damage types the character takes half damage from 

level = player level or challenge rating 

spell manager = if the creatures is a spell caster, this will include spell casting info along with spells known 

makes death saves = whether the creature dies when at 0 hp, or becomes uncious instead 

 
 ### Features 
 Features are properites that are static to a creature. These can be added from either class, race, or other origins. They have a range of effect including how attack throws or saving throws are made, how much damage an attack can cause, or what happens when a creature drops to 0. A full list of implemented features are available in the FeatureCateglog.py file. This represents a sample of the total features in DnD 5e.  

### Action 
A action is something a creature can do on it's turn. It must have a avail_actions method that gives every combination of action and movement possible given a creature, in the form of (new_position, action). Actions are given as new instances of a action object. 

#### Attack 
An attack has 4 main properties. 

Modifier: How much is added to a 1d20 hit roll. This value must beat the target's AC to inflict damage 

Damage Dice: This is a string in the form of "2d8 + 6" that tells how much and what value of dice should be rolled to deal damage. This will be rolled each time damage is done. 

Distance: This is how far from the creature the attack can reach. There is also an optional parameter for min_distance which tells the smallest distance a creature can be from creature for attack to work. 

Side-effects: Additional conditions that can be inflicted on a creature if hit with the attack 

#### Spells 
There are a selection of spells implemented in this simulation, implmeneted in SpellBook.py 

There are the following categories of spells: 

* Healing: adds hp to a creature 

* Attack: deals an ordinary attack to a creature 

* Attack with save: an ordinary attack, but a saving throw is made instead  

* Area of Effect: deals damage or adds a condition to an area of the map  

* Attack Bonus: Add extra damage to next attack(s)

* Target Creature: Adds extra damage when a particular creature is targeted  

* Defense: adds to the AC of a creature  

* Saving throw 



## Monster Manual 
Monsters up to level one in the monster manual are implemented in this simulation. A represenation of them are available in the monster_manual.txt, which can be loaded if the MonsterManual.py program is implemented. Not not all monsters are fully implemented, as noted in the "fully_impl" attritubute of the monster. Currently around 30% of the monster manual is fully implemented, however some of the partially implemented monsters only have minor differences. 

## Player Characters 
A sample of player characters are available in the player_files.txt file and are loaded into the mannual when MonsterManual.py is run. More characters can be created by running the CreateCharacter.py program and entering player information. Note that player names must be unique. 

## Agents 

There are four different classes that are children of the creature class implemented. Each use a different method for deciding turns. 

### Human
This allows a user to input what actions they want to preform. This currently is only useful for debugging purposes, and the UI can be difficult to interpret. 

### Random 
This agent randomly chooses a available action. 

### Aggressive 
This is a rule based agent that chooses the movement and action combination that get's closest to an enemy and attacks with it's strongest weapon. 

### JinJerry 
This is based an algorithm from a general video game playing competition that is based on Monte Carlo search. It random simulates a random game following each possible action and evaluates the success of each. 

### Shyne 
This is an improvement made on the JinJerry algorithm that allows for multiple simulation while also eliminating poor preforming actions. 

## Using the Simulator 

### CreateCharacter 
This provides a way for a user to enter information about a character to be added to the player stats file and loaded into a manual. 

### AutomaticPlayTestingUSer 
Here a user can preform a playtesting trial by providing the names of monsters and players available in the monster or player manual, which agent class to use, and how many games to play. At the end of the playtesting games statistics, such as average total damage (as a ratio to max HP) for the games will be provided. 

### Tournament 
This has a function for having agent classes compete against each other. A tournament randomly creates two identical parties with the monster and player parties being constructed with the given classes. It then prints win results for the players and monsters. 

### Experiments  
This contains several experiments for comparing agent classes to each other. 

### PlayTestingExperiments 
This this automatically create playtesting situations and record results in the PlayTestingResults folder 

## Implementation programs 


### DnD Toolkit 
This holds all the necessary base classes to play a game of DnD in the simulator. It also includes several important constants such as damage type strings. 

### Creature Classes 
This implements the base creature class. 

### Basic Agents 
This file contains the Human, Aggressive, and Random agent classes. 

### JinJerry 
This contains the class for a JinJerry agent 

### Shyne 
This contains the ShyneCreature class. 

### Monster Manual 
 Each creature (both players and monsters) is represented as a dictionary where stats (such as HP) are given key values. This also provides a method to create a specific creature given a agent class. The dictionaries for all creatures is given in the MANUAL constant that is created, and player and monster creatures are provide in the MONSTER_MANUAL and PLAYER_MANUAL retrospectfully. 

 ### Features 
 This implement the feature manager and feature bases classes 

 ### Feature Catelog 
 This implements the indivuals features available in this simulation and packages them into the ALL_FEATURES constant.

 ### Conditions 
 This implements the conditions class along with all base conditions.   

 ### Spells 
 This implements the spell manager and spell base classes. 

 ### Spell Book 
 This implements the indivuals spells available in this simulation and packages them into the SPELL_BOOK constant. 

