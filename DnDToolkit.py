from cgitb import reset
from copy import deepcopy
import random

PLAYERTEAM = "player"
MONSTERTEAM = "monster"
TIE = "tie"
INCOMPLETE = "incomplete"


class Condition:
    def __init__(self, can_act, can_move, is_dead, making_death_saves):
        self.can_act = can_act
        self.can_move = can_move 
        self.is_dead = is_dead 
        self.making_death_saves = making_death_saves 

# Set up conditions 
AWAKE = Condition(True, True, False, False)
DEAD = Condition(False, False, True, False)
ASLEEP = Condition(False, False, False, True)
STABLE = Condition(False, False, False, False)

class Dice:
    def __init__(self, dice_string) -> None:
        """
        Takes a string in the form of '2d8 + 4' and 
        converts it into the appropriate dice roll
        """
        self.dice_string = dice_string 
        d_index = dice_string.find("d")
        space_index = dice_string.find(" ", d_index)

        self.amount = int(dice_string[:d_index]) 

        # if there is not a space, there isn't a modifier 
        if space_index == -1: 
            self.type = int(dice_string[d_index +1:]) 
            self.modifer = 0 
        else:
            self.type = int(dice_string[d_index + 1: space_index]) 
            
            next_space = dice_string.find(" ", space_index + 1) # corresponding to space before modifier
            # modifier is positive
            if dice_string.find("+") != -1: 
                self.modifer = int(dice_string[next_space:]) 
            # modifier is negative 
            elif dice_string.find("-") != -1:
                self.modifer = -int(dice_string[next_space:]) 
            #something has gone terrible wrong
            else:
                self.modifer = 0

    def roll(self):
        """
        return result of one roll 
        """
        amount = self.modifer

        for i in range(self.amount):
            amount += random.randint(1, self.type)
            
        
        return amount 

    def __str__(self):
        return self.dice_string

class Creature:
    def __init__(self, ac, hp, speed, position = (0,0), name = "Creature", team = "neutral", actions = [], rolled = False):
        """
        Initialize a creature 
        ac = numerical armor class 
        hp = max hit points either as value or dice roll, depending on rolled value 
        position = starting position as a tuple of row and column 
        name = name of creature 
        team = what side creatures fights for, decides who is an enemy or friend 
        action = available actions as a list 
        rolled = whether hp is rolled or static 
        """
        self.ac = ac 

        if rolled:
            self.hp_dice = Dice(hp)
            hp = self.hp_dice.roll()  
        
        self.max_hp = hp 
        self.hp = self.max_hp # assumes we start with full health  
        self.condition =  AWAKE
        self.position = position 
        self.name = name 
        self.team = team 
        self.actions = actions 
        self.speed = speed 
        self.null = NullAction() 
        actions.append(self.null) # make sure the null action is included
        self.init_dice = Dice("1d20")
    
    def damage(self, amount):
        """
        deal damage to creature 
        """
        self.hp -= amount
        if self.hp <= 0: 
            self.zero_condition() 
    
    def roll_initiative(self):
        """
        Roll( for initative
        by default no modifications 
        """
        return self.init_dice.roll() 
    
    def zero_condition(self):
        """
        what happens when creature drops to 
        0 hp

        by default creatures dies, for 
        player they should fall unconcious
        and start making death saves 
        """
        self.hp = 0 # there is not negative HP 
        self.die()

    def avail_movement(self, grid):
        """
        all available movement within 
        walking speed 
        """

        if self.condition.can_move:
            movement = [self.position] 

            movement += [piece[1] for piece in grid.tiles_in_range(self.position, self.speed) if grid.is_free(piece[1])]
            return movement 
        else:
            return [self.position]

    def die(self):
        """
        when creatures is killed 
        """
        self.condition = DEAD
    
    def avail_actions(self, grid):
        """
        total available movmenent and 
        actions combinations 
        """
        if self.condition.can_act:
            total_actions = [] 
            for action in self.actions:
                total_actions += action.avail_actions(self, grid) 
            
            return total_actions
        else:
            return self.null.avail_actions(self, grid) 
    
    def turn(self, map, order, initiative):
        """
        return a movement and an action

        by default will choose first action
        """
        return self.avail_actions(map)[0]
    
    def long_rest(self):
        """
        reset stats, as if after 
        a long rest. 

        This can conquer death, unlike the real 
        game. 
        """

        self.hp = self.max_hp
        self.condition = AWAKE 
    
    def __str__(self):
        return self.name

class Action:
    def __init__(self, name):
        self.name = name 
    def __str__(self):
        return self.name 
    def execute(self):
        """
        implementation of execute varies by action
        """
        pass 

    def avail_actions(self, creature, grid):
        """
        return all the possible options 
        for all possible movement of a creature
        return move and action object pairs
        """
        return [(creature.position, self)]
    
    def __str__(self):
        return self.name 

class NullAction(Action):
    """
    doesn't do anything 
    """

    def __init__(self):
        super().__init__("No Action")
    
    def avail_actions(self, creature, grid):
        actions = []
        for move in creature.avail_movement(grid):
            actions.append((move, self))
        
        return actions 

class Attack(Action):
    def __init__(self, hit_bonus, damage_dice_string, dist, name = "Attack", target = None):
        """
        hit bonus = modifer to d20 roll for hit 
        damage_dice_string = damage dice written in the format "2d8" or "2d8 + 4" 
        """
        Action.__init__(self, name) 

        hit_dice_str = "1d20 + " + str(hit_bonus) 
        self.hit_bonus = hit_bonus 
        self.hit_dice = Dice(hit_dice_str)
        self.damage_dice = Dice(damage_dice_string)
        self.target = target 
        self.dist = dist 
    
    def execute(self):
        """
        Excute attack on target
        if target is none, do nothing
        """
        # if there is not a target, dont do anything 
        if not self.target is None: 
            hit = self.hit_dice.roll() # roll hit dice 

            # if hit succeeds, deal damage 
            if hit >= self.target.ac: 
                self.target.damage(self.damage_dice.roll())

    def set_target(self, target):
        """
        Assign target 
        """
        self.target = target 
    
    def avail_targets(self, team, position, grid):
        """
        return a list of enemies within 
        range of attack
        """

        return [enemy for enemy in grid.enemies_in_range(team, position, self.dist) if not enemy.condition.is_dead] 
    
    def avail_actions(self, creature, grid):
        actions = [] 

        for move in creature.avail_movement(grid):
            

            targets = self.avail_targets(creature.team, move, grid)

            for target in targets:
                new_action = Attack( self.hit_bonus, str(self.damage_dice), self.dist, self.name, target = target)
                actions.append((move, new_action))
        
        return actions 
    
    def __str__(self):
        if self.target != None:
            return "Attack " + str(self.target) + " with " + self.name 
        else: 
            return self.name 

class Grid():
    def __init__(self, height, width, space = 10):
        self.height = height
        self.width = width 
        self._make_grid() 
        self.space = space
        self.pieces = []  
    
    def _make_grid(self):
        """
        initialize grid with None values 
        """
        self.grid = [] 
        for row in range(self.height):
            self.grid.append([None] * self.width)
    
    def is_free(self, position):
        """
        return true if a position is free 
        """
        return self.grid[position[0]][position[1]] is None 

    def clear_position(self, position):
        """
        sets position to None 
        """
        self.grid[position[0]][position[1]] = None

    def clear_grid(self):
        for piece in self.pieces: 
            self.clear_position(piece.position)
        
        pieces = [] 

    def place_piece(self, piece, position):
        """
        place a piece in the grid at given position 

        pieces must have .position value 
        """

        # only place piece if space is empty 
        if self.is_free(position): 
            self.pieces.append(piece)
            self.grid[position[0]][position[1]] = piece 
    
    def place_pieces(self, pieces):
        """
        place a list of pieces in the grid
        assumes each piece has a .position value
        """

        for piece in pieces:
            self.place_piece(piece, piece.position)
    
    def move_piece(self, piece, new_pos):
        """
        move a piece to a new position
        assumes that piece has a .position 
        value
        """

        cur_pos = piece.position 
        self.clear_position(cur_pos) 
        self.grid[new_pos[0]][new_pos[1]] = piece 
        piece.position = new_pos 
    
    def remove_piece(self, piece):
        """
        remove a piece from the grid
        assumes piece is on grid
        """
        self.clear_position(piece.position)
        self.pieces.remove(piece)        
    
    def distance(self, pos1, pos2):
        """
        distance between two points in the grid
        assumes both positions are valid 
        """
    
        width = abs(pos1[0] - pos2[0])
        height = abs(pos1[1] - pos2[1])
        return width + height 
    
    def tiles_in_range(self, position, dist):
        """
        return a list of tuples of all tiles and positions that are 
        within range of a given position 

        This works by scanning through a box with length 2 range
        centers at poistion, and adding all pieces that are within the 
        distance describes
        """

        posx = position[1]
        posy = position[0]

        left_x = max(posx - dist, 0) # smallest x value of box, must be on grid
        right_x = min(posx + dist, self.width -1) # largest x of max, must be on grid 

        top_y = max(posy - dist, 0)
        bottom_y = min(posy + dist, self.height - 1)
        
        tiles = [] 
        # check every value in the box
        for row in range(top_y, bottom_y + 1):
            for col in range(left_x, right_x + 1):
                new_pos = (row, col)
                if self.distance(position, new_pos) <= dist:
                    tiles.append((self.grid[row][col], (row, col)))
        
        return tiles 
    
    def pieces_in_range(self, position, dist):
        """
        Return as pieces that are in range of 
        a position 

        cycles through all pieces and adds the ones 
        that are within the distance. This assumes 
        that they are going to be less total pieces 
        than total tiles in range of position 
        """

        in_range = [] 

        for piece in self.pieces:
            if self.distance(position, piece.position) <= dist:
                in_range.append(piece)
        
        return in_range 

    
    def enemies_in_range(self, team, position, dist):
        """
        return all enemies of team (anyone who is not in same team)
        given a position and a range 
        """


        all_pieces = self.pieces_in_range(position, dist)
        enemies = [] 

        for piece in all_pieces:
            try: 
                piece_team = piece.team
                
                if piece_team != team:
                    enemies.append(piece)
            except: # not a creature 
                pass 
        
        return enemies 
    
    def clear_dead(self):
        """
        remove all dead creatures 
        """
        for piece in self.pieces:
            try: 
                if piece.condition.is_dead: 
                    self.remove_piece(piece)
            except: # not a creature 
                pass


    def __str__(self):
        return_str = ""

        for row in range(self.height):
            return_str += "|"
            for col in range(self.width):
                piece_string = str(self.grid[row][col]) 

                if piece_string == "None":
                    piece_string = " "


                if len(piece_string) < self.space:
                    piece_string += " " * (self.space - len(piece_string))
                elif len(piece_string) > self.space:
                    piece_string = piece_string[:self.space]

                return_str += piece_string

                
                return_str += " | "
            if row != self.height - 1:
                return_str += "\n"
        
        return return_str 

class Game():
    def __init__(self, players, monsters, player_pos, monster_pos, map):
        """
        set up game given a list of monsters, players 
        and a starting map  
        """

        self.monsters = monsters 
        self.players = players  
        self.map = map 
        self.player_pos = player_pos 
        self.monster_pos = monster_pos 

        self.reset() 

    def set_up_board(self):
        """
        clear map, set staring positions, add monsters
        and players to grid 

        assumes that player pos is the same size 
        of player, and that mosnter pos is the same size 
        of monsters 
        """
        self.map.clear_grid() 

        for i,monster in enumerate(self.monsters):
            monster.position = self.monster_pos[i]
        
        for i,player in enumerate(self.players):
            player.position = self.player_pos[i]
        
        self.map.place_pieces(self.monsters)
        self.map.place_pieces(self.players)


    def set_teams(self):
        """
        make sure all teams are set correctly 
        """

        for player in self.players: 
            player.team = PLAYERTEAM
        
        for monster in self.monsters:
            monster.team = MONSTERTEAM
    
    def team_defeated(self, party):
        """
        return true if all of one team 
        is dead or unable to move and make 
        actions 
        """
        defeated = True
        
        i = 0 

        while defeated and i < len(party):
            if party[i].condition.can_act or party[i].condition.can_move:
                defeated = False 
            i += 1 
        
        return defeated 
    def long_rest(self):
        """
        reset all monster and 
        player stats 
        """

        for monster in self.monsters:
            monster.long_rest() 
        
        for player in self.players:
            player.long_rest() 
        

    def roll_initiative(self, debug = False):
        initiative = [(monster.roll_initiative(), monster) for monster in self.monsters]
        initiative += [(player.roll_initiative(), player) for player in self.players]

        initiative.sort(key = lambda x: x[0])

        if debug: 
            for i in initiative:
                print("Monster: {}, Initaitve: {}".format(i[1], i[0]))
        
        return [init[1] for init in initiative]
    
    def display_health(self):

        print("----------" + MONSTERTEAM + " health-------------")
        monster_health = ""

        for monster in self.monsters: 
            monster_health += " {} : {} ".format(monster, monster.hp)
        
        print(monster_health)
        
        print("----------" + PLAYERTEAM + " health-------------")
        player_health = ""

        for player in self.players: 
            player_health += " {} : {} ".format(player, player.hp)
        print(player_health)
    
    def reset(self):
        self.set_teams() 
        self.set_up_board()
        self.long_rest() 
        self.order = self.roll_initiative() 
        self.turn = 0 
        self.round = 0 
    
    def create_copy(self):
        return deepcopy(self)
    
    def next_creature(self):
        return self.order[self.turn]
    
    def update_init(self):
        creature = self.next_creature()
        self.turn += 1 

        # top of init
        if self.turn >= len(self.order):
            self.turn = 0 
            self.round += 1 
        return creature 
    
    def get_winner(self):
        monster_defeat = self.team_defeated(self.monsters)
        player_defeat = self.team_defeated(self.players)

        if monster_defeat and not player_defeat:
            return PLAYERTEAM
        elif player_defeat and not monster_defeat:
            return MONSTERTEAM 
        elif monster_defeat and player_defeat:
            return TIE
        else:
            return INCOMPLETE 
        
    def next_turn(self, creature, action, debug):
        """
        complete a turn given a creature 
        and an action
        """
        if creature.condition.can_move or creature.condition.can_act: 

            #move creature 
            self.map.move_piece(creature, action[0])

            # complete actions 
            action[1].execute()

            if debug:
                print("\n {}'s Turn".format(creature))
                print(self.map)
                print("Action: {} ".format(action[1])) 
                print("\n")
                self.display_health()
                print("\n")

            self.map.clear_dead() 

    def play_game(self, round_limit = 50, debug = False):
        self.reset() 

        if debug:
            print(self.map)

        while self.get_winner() == INCOMPLETE and self.round < round_limit:
            creature = self.update_init() 
            action = creature.turn(map = self.map, order = self.order, initiative = self.turn) 
            self.next_turn(creature, action, debug) 
        
        winner = self.get_winner() 
        
        return winner, self.round  


if __name__ == "__main__":
    sword = Attack(4, "2d8", 1, name = "Sword")
    arrow = Attack(hit_bonus= 0, dist= 5, damage_dice_string="1d6", name = "Bow and Arrow")
    monster = Creature(ac =12, hp =30, speed = 3, name = "Fuzzy Wuzzy", team = "player", actions=[sword])
    monster3 = Creature(12, 30, 3, name = "Leo", team = "player", actions=[arrow])
    monster2 = Creature(12, 30, 3, name = "Bear", team = "monster", actions=[sword])
    map = Grid(5,5)
    map.place_pieces([monster, monster2])
    null = NullAction()

    player_pos = [(4,4), (3,4)]
    monster_pos = [(0,0)]

    #print(map)
    #print("\n\n")
    
    game = Game(players=[monster, monster2], monsters = [monster3], player_pos=player_pos, monster_pos= monster_pos, map=map)
    print(game.play_game(debug=True))
    

