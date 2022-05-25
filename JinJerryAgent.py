from DnDToolkit import * 
from BasicAgents import * 

class JinJerryCreature(Creature):
    def __init__(self, ac, hp, speed, position=..., name="Creature", team="neutral", actions=..., rolled=False):
        super().__init__(ac, hp, speed, position, name, team, actions, rolled)
    
    def forward_model(self, map, creature, turn):
        """
        simulates a next turn given a turn 
        a creature to preform that turn

        assumes that map is a copy 
        and not the main game map
        """

        #TODO figure out way to abstact this 

        #move creature 
        map.move_piece(creature, turn[0])

        # complete actions 
        turn[1].execute()

        return map 

    def decide_action(self, grid, creature):
        """
        choices how the model 
        decides on an action

        by default is random 
        """

        actions = creature.avail_actions(grid) 
        return random.choice(actions)
    
    def get_hp_ratio(self, creatures, team, equal = True):
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
        return cur_hp / max_hp 

    
    def static_evaluator(self, grid, order):
        """
        return an estimation of how well 
        our team is doing given a 
        grid and an order
        """
        #print("Team: {}, my hp:{}, their hp: {}".format(self.team, self.get_hp_ratio(order, self.team), self.get_hp_ratio(order, self.team, equal=False) ))
        return self.get_hp_ratio(order, self.team) - self.get_hp_ratio(order, self.team, equal=False)

    def create_game_copy(self, map, order):
        """
        create a copy of the game 
        TODO: Move this out of agent 
        """
 
        order_copy = copy.deepcopy(order)
        map_copy = copy.deepcopy(map)

        #this may be the jankyiest solution but..... 
        map_copy.clear_grid() 
        map_copy.place_pieces(order_copy)

        return map_copy, order_copy


        
    def simulate_game(self, map, initiative, order, depth_limit = 4):
        """
        simulate a game given depth of 4 
        return the resulting map 

        initiative is the creature going 
        next 

        Assumes that map and order are copies 
        """
        depth = 0 

        while depth < depth_limit:
            creature = order[initiative]
            turn = self.decide_action(map, creature)
            map = self.forward_model(map, creature, turn)
            initiative += 1 
            if initiative >= len(order):
                initiative = 0 
            
            depth += 1 
        return map, order
    
    def turn(self, map, initiative, order):
        options = self.avail_actions(map) 

        options_evaluations = [] 

        for option in options: 

            # create a copy of game 
            map_copy, order_copy = self.create_game_copy(map, order)


            # do action in game 
            self.forward_model(map_copy, self, option)


            # evaluate option 
            action_value = self.static_evaluator(map_copy, order)

            next_init = (initiative + 1) % len(order_copy) 

            # forward simulate 
            map_copy, order_copy = self.simulate_game(map = map_copy, initiative= next_init, order = order_copy)


            # evualute future model 
            next_value = self.static_evaluator(map_copy, order_copy)


            # this turns value is the max of first eval and future eval 
            options_evaluations.append((max(action_value, next_value), option))
        
        options_evaluations.sort(key = lambda x: x[0]) # sort by eval 

        return options_evaluations[0][1]



if __name__ == "__main__":
    sword = Attack(3, "2d6", 10, name = "Sword")
    bow = Attack(hit_bonus=0, damage_dice_string= "1d4", dist = 10, name = "Bow and Arrow")

    # players 
    ducky = JinJerryCreature(12, 20, 3, actions=[sword], name = "Rubber Ducky")
    elmo = JinJerryCreature(12, 20, 3, actions = [bow], name = "Elmo")

    # monsters 
    bear = RandomCreature(12, 20, 3, actions = [sword], name = "Bear")
    fuzzy = RandomCreature(12, 20, 3, actions = [bow], name = "Fuzzy Wuzzy")

    grid = Grid(6, 6, space = 3)

    monster_pos = [(0,0), (0,1)]
    player_pos = [(5,5), (5,4)]

    game = Game(players = [ducky, elmo], monsters = [fuzzy, bear],map = grid, player_pos=player_pos, monster_pos=monster_pos)
    #game.set_up_board(player_pos, monster_pos)
    player_wins = 0 
    monster_wins = 0 
    ties = 0 

    for i in range(20):
        winner = game.play_game(debug=False)[0]
        if winner == PLAYERTEAM:
            player_wins += 1 
        elif winner == MONSTERTEAM:
            monster_wins += 1 
        else:
            ties += 1 

    
    print("Player wins: {}, Monster wins: {}, Ties:{}".format(player_wins, monster_wins, ties))






