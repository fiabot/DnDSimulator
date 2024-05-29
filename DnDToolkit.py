from copy import deepcopy
import copy
import random
import time


# constants 
PLAYERTEAM = "player"
MONSTERTEAM = "monster"
TIE = "tie"
INCOMPLETE = "incomplete"

STR_STR = "strength"
DEX_STR = "dexerity"
CON_STR = "constitution"
INT_STR = "intelligence"
WIS_STR = "wisdom"
CHAR_STR = "charisma"

SAVES_STR = "saves"
FAIL_STR = "fail"

MELE = "melee"
RANGED = "ranged"

SLASHING_DAMAGE = "slashing"
PIERCING_DAMAGE = "piercing"
BLUDGEONING_DAMAGE = "bludgeoning" 
POISON_DAMAGE = "posion"
ACID_DAMAGE = "acid"
FIRE_DAMAGE = "fire"
COLD_DAMAGE = "cold"
RADIANT_DAMAGE = "radiant" 
NECROTIC = "necrotic"
LIGHTNING = "lightning" 
THUNDER = "thunder"
FORCE_DAMAGE = "force"
PYSCHIC_DAMAGE = "psychic" 

def set_positions(num_pcs, num_mons):
    player_pos = []
    monster_pos = [] 
    for i in range(num_mons):
            monster_pos.append((0, i)) # monsters at top left 
    
    for i in range(num_pcs): 
        player_pos.append((7 - 1, 7 - i - 1)) 
    
    return player_pos, monster_pos 

def free_moves(speed, creature, game):
    """
    Get all the available moves given
    a creature and a move speed 
    """
    grid = game.map 
    movement = [creature.position] 

    movement += [piece[1] for piece in grid.tiles_in_range(creature.position, speed) if grid.is_free(piece[1])]
    return movement 

def make_dice_string(amount, type, modifer = 0):
    """
    make a dice string givne 
    amount type and modifer 
    """
    return_str = "{}d{}".format(amount, type)
    if(modifer > 0):
        return_str += " + {}".format(modifer)
    elif (modifer < 0):
        return_str += " - {}".format(abs(modifer))
    
    return return_str

def is_friend(creature, other):
    """
    return true if creature is a 
    friend 
    """
    try: 
        return creature.team == other.team 
    except:
        False 

def make_unqiue(creatures):
    """
    make all creatures have 
    unique names 
    """

    names = {}

    for creature in creatures: 
        name = creature.name 
        if name in names:   
            creature.name = name + str(names[name]) 
            names[name] += 1 
        else:
            names[name] = 1


class Dice:
    def __init__(self, dice_string, advantage = 0) -> None:
        """
        Takes a string in the form of '2d8 + 4' and 
        converts it into the appropriate dice roll

        Will also take a default advantage 
        """
        self.dice_string = dice_string 
        d_index = dice_string.find("d")
        space_index = dice_string.find(" ", d_index)
        plus_index = dice_string.find("+") 
        minus_index = dice_string.find("-")
        if d_index != -1: 
            self.amount = int(dice_string[:d_index]) 

              # if there is not a space, there isn't a modifier 
            if space_index == -1 and plus_index == -1 and minus_index == -1: 
                self.type = int(dice_string[d_index +1:]) 
                self.modifer = 0 
            else:

                if space_index == -1:
                    mod_index = max(plus_index, minus_index)
                else:
                    mod_index = space_index 
                self.type = int(dice_string[d_index + 1: mod_index]) 

                
                if space_index == -1:
                    next_space = mod_index + 1
                else:
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
        else: 
            self.amount = 0 
            self.type = 0 
            self.modifer = int(dice_string)

      
        self.expected_value() 
        self.default_advantage = advantage 
    
    def expected_value(self):
        """
        The average expected 
        value of this dice 
        """
        one_roll = self.type // 2 + 0.5 
        total_roll = one_roll * self.amount 
        self.expected = total_roll + self.modifer 
        return self.expected 

    def one_roll(self):
        """
        return result of one roll 
        """
        amount = self.modifer

        for i in range(self.amount):
            amount += random.randint(1, self.type)
            
        
        return amount 
    
    def roll(self, advantage = None):
        """
        roll dice

        if advantage is none, use 
        default advantage 

        otherwise apply advantage 

        roll with advantage > 0 
        roll with no advantage = 0 
        roll with disadvantage < 0 
        """
        if advantage is None: 
            advantage = self.default_advantage 
        
        first_roll = self.one_roll()

        if (advantage != 0):
            second_roll = self.one_roll() 

            if (advantage < 0):
                return min(first_roll, second_roll)
            else: 
                return max(first_roll, second_roll) 
        else: 
            return first_roll 

    def __str__(self):
        ad_str = "no advantage"
        if self.default_advantage > 0: 
            ad_str = "advantage"
        elif self.default_advantage < 0: 
            ad_str = "disavantage"
        
        return "{} with {}".format(self.dice_string, ad_str)

class FailDice (Dice):
    """
    Dice that will return 
    0 always 
    """
    def __init__(self):
        super().__init__("0d20", 0) 

class CompoundDice: 
    """
    Dice with different kinds 
    of dice within it 
    """
    def __init__(self, dice_list) -> None:
        self.dice_list = dice_list
    
    def roll(self, advantage = None):
        total = 0 
        for die in self.dice_list: 
            total += die.roll(advantage)

        return total  

class Grid():
    """
    representation of 
    game map. 
    """
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
        """
        sets positions to None 
        and removes any pieces 
        """
        for piece in self.pieces: 
            self.clear_position(piece.position)
        
        self.pieces = [] 

    def place_piece(self, piece, position):
        """
        place a piece in the grid at given position 

        pieces must have .position value
        """

        # only place piece if space is empty 
        if self.is_free(position): 
            self.pieces.append(piece)
            self.grid[position[0]][position[1]] = piece 
            piece.position = position 
    
    def place_pieces(self, pieces):
        """
        place a list of pieces in the grid
        assumes each piece has a .position value
        with desired position 
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
    
    def tiles_in_range(self, position, dist_max, dist_min =0):
        """
        return a list of tuples of all tiles and positions that are 
        within range of a given position 

        This works by scanning through a box with length 2 range
        centers at poistion, and adding all pieces that are within the 
        distance describes
        """

        posx = position[1]
        posy = position[0]

        left_x = max(posx - dist_max, 0) # smallest x value of box, must be on grid
        right_x = min(posx + dist_max, self.width -1) # largest x of max, must be on grid 

        top_y = max(posy - dist_max, 0)
        bottom_y = min(posy + dist_max, self.height - 1)
        
        tiles = [] 
        # check every value in the box
        for row in range(top_y, bottom_y + 1):
            for col in range(left_x, right_x + 1):
                new_pos = (row, col)
                distance = self.distance(position, new_pos)
                if distance <= dist_max and distance >= dist_min:
                    tiles.append((self.grid[row][col], (row, col)))
        
        return tiles 
    
    def pieces_in_range(self, position, dist_max, dist_min = 0):
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
            distance = self.distance(position, piece.position) 
            if isinstance(distance, str):
                print("ERROR: distance with value {}".format(distance))
            if isinstance(dist_max, str):
                print("ERROR: dist max with value {}".format(dist_max))
            if isinstance(dist_min, str):
                print("ERROR: dist min with value {}".format(dist_min))
            if distance <= dist_max and distance >= dist_min:
                in_range.append(piece)
        
        return in_range 

    def closest_enemy(self, team, position):
        """
        return the closest enemy to a creature 
        """
        closet_enemy = None
        closet_dist = float("inf")
        for piece in self.pieces: 
            try: 
                if piece.team != team and self.distance(position, piece.position) < closet_dist:
                    closet_dist = self.distance(position, piece.position)
                    closet_enemy = piece 
            except: 
                pass 
        return closet_enemy 

    def enemies_in_range(self, team, position, dist, dist_min = 0):
        """
        return all enemies of team (anyone who is not in same team)
        given a position and a range 
        """


        all_pieces = self.pieces_in_range(position, dist, dist_min=dist_min)
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
                if not piece.is_alive(): 
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

        if monster and player names are unique
        there names will be changed 
        """
        make_unqiue(players)
        make_unqiue(monsters)
        self.monsters = monsters 
        self.players = players  
        self.map = map 
        self.player_pos = player_pos 
        self.monster_pos = monster_pos 
        self.create_dict() 
        self.games_played = 0
        self.stat_log = []     

       

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
    
    def create_dict(self):
        """
        Create a dicitonary 
        to look up creatures 
        in game 
        """
        self.all_creatures = {} 
        for monster in self.monsters:
            self.all_creatures[monster.name] = monster
        
        for player in self.players:
            self.all_creatures[player.name] = player

    def get_creature(self, name):
        """
        return a creature given a name 

        returns none if creature not in game
        """

        if name in self.all_creatures:
            return self.all_creatures[name]
        else: 
            return None 

    
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
            if party[i].can_act() or party[i].can_move():
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
        """
        roll intative for all 
        creature and set order 
        """
        initiative = [(monster.roll_initiative(), monster) for monster in self.monsters]
        initiative += [(player.roll_initiative(), player) for player in self.players]

        initiative.sort(key = lambda x: x[0])

        if debug: 
            for i in initiative:
                print("Monster: {}, Initaitve: {}".format(i[1], i[0]))
        
        return [init[1] for init in initiative]
    
    def display_health(self):
        """
        display health info 
        for all creatures in game 
        """
        print("----------" + MONSTERTEAM + " status-------------")
        monster_health = ""

        for monster in self.monsters: 
            monster_health += "\n {} : (hp: {}, can move : {}, can act : {}) ".format(monster, monster.hp, monster.can_move(), monster.can_act())
        print(monster_health)
        
        print("----------" + PLAYERTEAM + " health-------------")
        player_health = ""

        for player in self.players: 
            player_health += "\n {} : (hp: {}, can move : {}, can act : {}) ".format(player, player.hp, player.can_move(), player.can_act())
        print(player_health)
    
    def reset(self):
        """
        reset game state 
        to starting state 
        """
        self.set_teams() 
        self.set_up_board()
        self.long_rest() 
        self.order = self.roll_initiative() 
        self.turn = 0 
        self.round = 0 
        self.turn_log = [] 
        
        self.stats = {"success": 0, "total damage" : 0, "normalized damage": 0, "ending health": 0, 
                    "deaths": 0, "amount asleep": 0, "spells": 0, "time":0} 
        
    
    def create_copy(self):
        """
        return a copy of the game 
        """
        new_game = deepcopy(self)

        # With deep copy the pieces on
        # the grid are not the pieces 
        # in the player 
        new_game.map.clear_grid() 
        new_game.map.place_pieces(new_game.monsters)
        new_game.map.place_pieces(new_game.players)

        return new_game 
    
    def next_creature(self):
        """
        get creature next on intiative 
        """
        return self.order[self.turn]
    
    def update_init(self):
        """
        update current place 
        in initative 
        """
        creature = self.next_creature()
        self.turn += 1 

        # top of init
        if self.turn >= len(self.order):
            self.turn = 0 
            self.round += 1 
        return creature 
    
    def get_winner(self):
        """
        return which team won 
        or if game is incomplete or 
        tied 
        """
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
            
    def is_terminal(self):
        winner = self.get_winner()
        return winner == PLAYERTEAM or winner == MONSTERTEAM 

        
    def next_turn(self, creature, action, debug = False, log = False):
        """
        complete a turn given a creature 
        and an action
        """
        if creature.can_move() or creature.can_act(): 

            #find enemies in threatened area 
            enemies_in_range = self.map.enemies_in_range(creature.team, creature.position, 1)

            #move creature 
            self.map.move_piece(creature, action[0])

            #See if creature triggered opp attack 
            for enemy in enemies_in_range: 
                if self.map.distance(creature.position, enemy.position) > 1:
                    enemy.opportunity_attack(creature, self)
                    if (debug):
                        print("{} got an opportunity attack on {}".format(enemy.name, creature.name))

            # complete actions 
            action[1].execute(self, debug = debug)

            creature.end_of_turn(self) 

            if debug:
                print("\n {}'s Turn".format(creature))
                print(self.map)
                print("Action: {} ".format(action[1])) 
                print("\n")
                self.display_health()
                print("\n")
            if log:
                self.turn_log.append([self.round, creature.name, action[0], action[1].name, str(self.map)])

            self.map.clear_dead() 

    def get_damage_stats(self):
        """
        Get damage and health 
        data for the players 
        in the game for 
        game log 
        """
        max_health = 0 
        total_damage = 0 
        current_health = 0 
        deaths = 0 
        uncons_amount = 0 
        total_spells = 0 
        spells_used = 0 

        for player in self.players:
            max_health += player.max_hp 
            total_damage += player.damage_taken 
            current_health += player.hp 
            uncons_amount += player.uncons_amount 
            if not player.features.is_alive():
                deaths += 1 
            if not player.spell_manager is None:
                total_spells += player.spell_manager.total_spell_slots
                spells_used += player.spell_manager.total_spell_slots - player.spell_manager.current_spell_slots
        
        if total_spells == 0:
            percent_spells = 0
        else:
            percent_spells = spells_used / total_spells
        
        return total_damage / len(self.players),  total_damage / max_health , current_health / max_health, deaths, uncons_amount, percent_spells
   
    def set_stats(self, winner, time):
        """
        set current game stats 
        and add them to stat log 
        """
        if winner == PLAYERTEAM:
            self.stats["success"] += 1 
        self.stats["time"] = time 
        total_damage, norm_damage, health, deaths, uncons_amount, spells   = self.get_damage_stats()
        self.stats["amount asleep"] = uncons_amount 
        self.stats["total damage"] = total_damage 
        self.stats["normalized damage"] = norm_damage 
        self.stats["ending health"] = health 
        self.stats["spells"] = spells 
        if winner != PLAYERTEAM:
            self.stats["deaths"]  = len(self.players)
        else:
            self.stats["deaths"] = deaths 

        
        self.stat_log.append(copy.copy(self.stats))

    def get_average_stats(self):
        """
        return the average stats for the 
        game 
        """
        ave_stats = {}
        for key in self.stats:
            stat_list = [stat[key] for stat in self.stat_log]
            ave_stats[key] = sum(stat_list) / len(stat_list)
        
        return ave_stats

    def play_game(self, round_limit = 50, debug = False, log = True, reset = True):
        """
        play one game 
        and return the winner 
        and how many rounds were completed 
        """
        if reset: 
            self.reset() 
        start = time.perf_counter()

        if debug:
            print(self.map)

        while self.get_winner() == INCOMPLETE and self.round < round_limit:
            creature = self.update_init() 
            action = creature.turn(game = self) 
            self.next_turn(creature, action, debug, log) 

        end  = time.perf_counter()
        winner = self.get_winner() 
        self.games_played += 1 

        self.set_stats(winner, end - start)
        
        return winner, self.round  

if __name__ == "__main__":
    print(make_dice_string(2, 8, 4))
    print(make_dice_string(2, 8))