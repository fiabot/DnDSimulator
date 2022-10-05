from copy import deepcopy
import random


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
    return_str = "{}d{}".format(amount, type)
    if(modifer > 0):
        return_str += " + {}".format(modifer)
    elif (modifer < 0):
        return_str += " - {}".format(abs(modifer))
    
    return return_str

def is_friend(creature, other):
    try: 
        return creature.team == other.team 
    except:
        False 

class Dice:
    def __init__(self, dice_string, advantage = 0) -> None:
        """
        Takes a string in the form of '2d8 + 4' and 
        converts it into the appropriate dice roll
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
    def __init__(self):
        super().__init__("0d20", 0) 

class CompoundDice: 
    def __init__(self, dice_list) -> None:
        self.dice_list = dice_list
    
    def roll(self, advantage = None):
        total = 0 
        for die in self.dice_list: 
            total += die.roll(advantage)

        return total  

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

        monster and player names must be unqiue 
        """

        self.monsters = monsters 
        self.players = players  
        self.map = map 
        self.player_pos = player_pos 
        self.monster_pos = monster_pos 
        self.create_dict() 

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
        initiative = [(monster.roll_initiative(), monster) for monster in self.monsters]
        initiative += [(player.roll_initiative(), player) for player in self.players]

        initiative.sort(key = lambda x: x[0])

        if debug: 
            for i in initiative:
                print("Monster: {}, Initaitve: {}".format(i[1], i[0]))
        
        return [init[1] for init in initiative]
    
    def display_health(self):

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
        self.set_teams() 
        self.set_up_board()
        self.long_rest() 
        self.order = self.roll_initiative() 
        self.turn = 0 
        self.round = 0 
    
    def create_copy(self):
        new_game = deepcopy(self)

        # With deep copy the pieces on
        # the grid are not the pieces 
        # in the player 
        new_game.map.clear_grid() 
        new_game.map.place_pieces(new_game.monsters)
        new_game.map.place_pieces(new_game.players)

        return new_game 
    
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
        
    def next_turn(self, creature, action, debug = False):
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

            self.map.clear_dead() 

    def play_game(self, round_limit = 50, debug = False):
        self.reset() 

        if debug:
            print(self.map)

        while self.get_winner() == INCOMPLETE and self.round < round_limit:
            creature = self.update_init() 
            action = creature.turn(game = self) 
            self.next_turn(creature, action, debug) 
        
        winner = self.get_winner() 
        
        return winner, self.round  

if __name__ == "__main__":
    print(make_dice_string(2, 8, 4))
    print(make_dice_string(2, 8))