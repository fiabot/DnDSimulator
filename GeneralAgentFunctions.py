import random 

def random_action(game, creature):
        """
        choices how the model 
        decides on an action

        by default is random 
        """

        avail_moves = [] 
        while len(avail_moves) == 0:
            action = random.choice(creature.actions) 
            if not action is None:
                avail_moves = action.avail_actions(creature, game)

        return random.choice(avail_moves)


def hp_ratio(creatures, team, equal = True):
        """
        returns a teams hp as a 
        ratio of their max hp
        """
        max_hp = 0 
        cur_hp = 0 
        for creature in creatures: 
            if (creature.team == team and equal) or (creature.team != team and (not equal)):
                max_hp += creature.max_hp 
                cur_hp += creature.hp 
        if max_hp == 0:
            print("ZERO ERROR")
            for creature in creatures:
                print("CREATURE: {} with hp {}".format(creature.name, creature.max_hp))
        else:
            return cur_hp / max_hp 

def heuristic(creature, game):
        """
        return an estimation of how well 
        our team is doing given a 
        grid and an order of creatures s
        """
        creatures = game.order 
        return hp_ratio(creatures, creature.team) - 2* hp_ratio(creatures, creature.team, equal=False)

def forward_action(action, creature_name, game):
    """
    create a new game state 
    by applying action 
    to it 
    
    """
    copy = game.create_copy() 
    creature = game.get_creature(creature_name) 
    creature = copy.update_init() 
    copy.next_turn(creature, action)

    return copy 

def one_step(game):
    creature = game.update_init() 
    turn = random_action(game, creature)
    game.next_turn(creature, turn)
    is_terminal = game.is_terminal()
    return is_terminal 


def simulate_game(game, depth):
        """
        simulate a game given depth 
        return the resulting map 

        initiative is the creature going 
        next 

        Assumes that game is a copy, 
        and therefor will modify it  
        """
        cur_depth = 0 
        is_terminal = False 
        

        while cur_depth < depth and not is_terminal:
            is_terminal = one_step(game)
            
            cur_depth += 1 
        return game