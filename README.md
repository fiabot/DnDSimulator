# DnDSimulator

DnD simulator with game-playing agents for automatic play testing. 

## Simulation 
This is a prototype version of a DnD encounter simulator. It currently allows creatures to complete one movement and one action (in that order) per turn. The movement available is determined by a speed, which determine how many spaces a creature can move in a turn. The way I implemented it, a space is worth 10 ft, but it would be easy to make this larger or smaller. The only action available current is attack, where the attacking creature rolls (with a bonus) to beat their opponents AC. The game runs until all of one party is dead (at 0 hp) or a turn limit is reached. The turn limit was determined by the thrown food theory, which is the estimated amount of time it would take for a party to be feed up with an encounter and decide to throw food at the GM. 

### Grid 
A grid (or map) is defined by a width and a height. Pieces can be added to the grid, as long as they have a position attribute. The grid class allows you to do things such as find the distance between two points, get the pieces that are in a range of position, or get the enemy closest to a creature. 

### Creature 
There are 4 main attributes of a creature: 

HP: The max amount of health that the creature can have and what health it has when it takes a long rest. This can be a discrete value or a dice string that is rolled. 

AC: This is the armor class of the creature, which signifies how difficult it is to damage the creature. 

Speed: This is how many tiles a creature can move in a turn. This is loosely related to 10ft in 5e. 

Actions: This is a list of actions available to a creature. They can choose from these actions and the NullAction (does nothing) when deciding on a action per turn. 

Every implementation of a creature must also have a turn method that decides what movement and action a creature makes given a game state. I talk below about what agents are implemented in this demo. 

### Action 
A action is something a creature can do on it's turn. It must have a avail_actions method that gives every combination of action and movement possible given a creature. Actions are given as new instances of a action object. 

#### Attack 
An attack has 3 main properties. 

Modifier: How much is added to a 1d20 hit roll. This value must beat the target's AC to inflict damage 

Damage Dice: This is a string in the form of "2d8 + 6" that tells how much and what value of dice should be rolled to deal damage. This will be rolled each time damage is done. 

Distance: This is how far from the creature the attack can reach. There is also an optional parameter for min_distance which tells the smallest distance a creature can be from creature for attack to work. 

Side-effects (such as a target being knocked prone) is not implemented in this simulation. Additionally 

## Monster Manual 
A very small subset is implemented in this simulation. The monsters were chosen based on what would be most easily represented in this simulation, along with having a range of challenge ratings and abilities.  

### Attacks (From least to most Powerful)

- Spear: range 0-6, damage: "1d6", hit: +2 
- Bite: range 0-1, damage: "1d4 + 2", hit + 4 
- scimitar: range 0-1, damage: 1d6 + 1
- shortsword: range: 1, damage: 1d6 + 2, hit +4 
- shortbow: range: 8-32, damage: 1d6+2, hit +4 
- ram: hit + 5, damage: 1d6 +3, range 0-1 
- javelin: hit: +5, damage: 1d6 + 3, distange: 3-12 
- crossbow: hit: +3, 1d8 + 1, range: 0-1
- longbow: hit: +3, damage: 1d8 +1, range: 15-60 
- claws: hit: +4, damage: 2d4 + 2, range: 0-1 
- midbite: hit + 2, damage: 2d6 + 2, range: 0-1
- great ax: hit + 5, damage: 1d12 + 3, range: 0-1 
- bigbitw: hit +5, damage: 2d6 + 3, range: 0-1 


### 1/8 Challenge Rating 
 
- Bandit: close and wide range weapons. HP of 11, and a AC of 12. Average speed.  
https://5thsrd.org/gamemaster_rules/monsters/bandit/

- Merfolk: moderate range weapon. HP of 11 and a AC of 11. Slow speed. 
https://5thsrd.org/gamemaster_rules/monsters/merfolk/ 

### 1/4 Challenge 
- Elk: close range attack. AC of 10 and a HP of 15. High speed.
https://5thsrd.org/gamemaster_rules/monsters/elk/ 

- Skeleton: short and very long range attack. AC of 13 and HP of 13. Average speed. 
https://5thsrd.org/gamemaster_rules/monsters/skeleton/

### 1/2 Challenge 
- Orc: close and wide range weapons. AC of 13 and HP of 15. Average speed.  
https://5thsrd.org/gamemaster_rules/monsters/orc/
- Gnoll: close mid and wide range attacks, AC of 15, HP of 22. Average speed. 
https://5thsrd.org/gamemaster_rules/monsters/gnoll/

### 1 Challenge 
- Dire Wolf: close range attack. AC of 14, HP of 37. High speed. 
https://5thsrd.org/gamemaster_rules/monsters/dire_wolf/ 
- Ghoul: Close attacks. HP of 22 and AC of 12. Average speed. 
https://5thsrd.org/gamemaster_rules/monsters/ghoul/ 

## Against Random 
With Depth 40 

Random: 0 

JinJerry: 0 

Tie: 10 

```
Game 0 of 10
Current results {'player': 0, 'monster': 0, 'tie': 0, 'incomplete': 0}
Party Size 4

Monsters:
gnoll
bandit
direwolf
direwolf1

Players:
gnoll1
bandit1
direwolf2
direwolf3
Time: 107.9137



Game 1 of 10
Current results {'player': 0, 'monster': 0, 'tie': 0, 'incomplete': 1}
Party Size 2

Monsters:
merfolf
orc

Players:
merfolf1
orc1
Time: 16.4300



Game 2 of 10
Current results {'player': 0, 'monster': 0, 'tie': 0, 'incomplete': 2}
Party Size 4

Monsters:
ghoul
direwolf
elk
orc

Players:
ghoul1
direwolf1
elk1
orc1
Time: 128.1549



Game 3 of 10
Current results {'player': 0, 'monster': 0, 'tie': 0, 'incomplete': 3}
Party Size 2

Monsters:
elk
direwolf

Players:
elk1
direwolf1
Time: 123.8873



Game 4 of 10
Current results {'player': 0, 'monster': 0, 'tie': 0, 'incomplete': 4}
Party Size 2

Monsters:
merfolf
bandit

Players:
merfolf1
bandit1
Time: 195.3344



Game 5 of 10
Current results {'player': 0, 'monster': 0, 'tie': 0, 'incomplete': 5}
Party Size 2

Monsters:
bandit
direwolf

Players:
bandit1
direwolf1
Time: 235.3669



Game 6 of 10
Current results {'player': 0, 'monster': 0, 'tie': 0, 'incomplete': 6}
Party Size 2

Monsters:
merfolf
ghoul

Players:
merfolf1
ghoul1
Time: 14.9650



Game 7 of 10
Current results {'player': 0, 'monster': 0, 'tie': 0, 'incomplete': 7}
Party Size 3

Monsters:
merfolf
gnoll
skeleton

Players:
merfolf1
gnoll1
skeleton1
Time: 736.2827



Game 8 of 10
Current results {'player': 0, 'monster': 0, 'tie': 0, 'incomplete': 8}
Party Size 3

Monsters:
bandit
skeleton
elk

Players:
bandit1
skeleton1
elk1
Time: 426.6754



Game 9 of 10
Current results {'player': 0, 'monster': 0, 'tie': 0, 'incomplete': 9}
Party Size 4

Monsters:
merfolf
ghoul
bandit
orc

Players:
merfolf1
ghoul1
bandit1
orc1
Time: 592.6483
{'player': 0, 'monster': 0, 'tie': 0, 'incomplete': 10}

```

### Against Aggressive 

#### Depth 40 

JinJerry: 3 

Aggressive: 3 

Tie: 4 

```
Games: 

Game 0 of 10 

Party Size 3
Monsters:
	orc
	elk
	gnoll
Time: 15.2008
Winner: Aggressive 

Game 1 of 10:

Party Size 3
Monsters:
	bandit
	skeleton
	bandit1
Time: 21.3690
Winner: Aggressive 

Game 2 of 10: 
Party Size 2
Monsters:
	bandit
	orc
Time: 23.7866
Winner: Aggressive 

Game 2 of 10: 
Party Size 4
Monsters:
	skeleton
	skeleton1
	ghoul
	ghoul1
Time: 104.3177
Winner: JinJerry

Game 4 of 10:
Party Size 2
Monsters:
	merfolf
	skeleton
Time: 50.7113
Winner: JinJerry


Game 5 of 10:
Party Size 2
Monsters:
	bandit
	bandit1
Time: 141.2515
Winner: Tie 


Game 6 of 10:
Party Size 2
Monsters:
	direwolf
	gnoll
Time: 148.0730
Winner: Tie 


Game 7 of 10:
Party Size 4
Monsters:
	merfolf
	skeleton
	gnoll
	skeleton1
Time: 192.6523
Winner: JinJerry 


Game 8 of 10:
Party Size 2
Monsters:
	merfolf
	ghoul
Winner: Tie

Game 9 of 10:
Party Size 2
Monsters:
	gnoll
	merfolf
Time: 113.3696
Winner: Tie 
```

