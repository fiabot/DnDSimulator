from DnDToolkit import * 
import copy 

class RandomCreature(Creature): 
    def __init__(self, ac, hp, speed, position=..., name="Creature", team="neutral", actions=..., rolled=False):
        super().__init__(ac, hp, speed, position, name, team, actions, rolled)
    
    def turn(self, map, initiative, order):
        return random.choice(self.avail_actions(map))

class HumanCreature(Creature):
    def __init__(self, ac, hp, speed, position=..., name="Creature", team="neutral", actions=..., rolled=False):
        super().__init__(ac, hp, speed, position, name, team, actions, rolled)

    def format_action (self, action):
        move = action[0]
        action = action[1]

        return "Move to {} and {}".format(move, action)

    def turn(self, map, initiative, order):
        actions = self.avail_actions(map)
        if not self.condition.is_dead:
            print("\n\n Current Map:")
            print(map)

            print("My Stats:")
            print(self.get_stats(self))

            end_intitative = initiative
            i = initiative + 1 
            if i >= len(order):
                    i = 0

            print("end: {}, start: {}".format(end_intitative, i)) 
            print("Next up on initiative:")
            while i != end_intitative: 

                print(self.get_stats(order[i]))
                if i >= len(order) -1:
                    i = 0
                else:
                    i += 1 

            print("\nAvailable Actions:")
            for i, action in enumerate(actions):
                print("{}: {}".format(i, self.format_action(action)))
            
            choice = int(input("What action do you want to take (write number): ")) 

            return actions[choice]
        else:
            print("\n\nLooks like you kicked the bucket. \nEnjoy the afterworld...")
            input("Press enter")
            return actions[0]
    
    def get_stats(self, creature):
        return_str = "Creature: {} \n".format(creature.name)
        return_str += "AC: {} \nHP: {} \n".format(creature.ac, creature.hp)
        return return_str


if __name__ == "__main__":
    sword = Attack(3, "2d6", 1, name = "Sword")
    bow = Attack(hit_bonus=0, damage_dice_string= "1d4", dist = 3, name = "Bow and Arrow")
    random1 = RandomCreature(12, 20, 3, actions=[sword], name = "Rubber Ducky")
    elmo = HumanCreature(12, 20, 3, actions=[bow], name = "Elmo")
    random2 = RandomCreature(12, 20, 3, actions = [bow], name = "Fuzzy Wuzzy")
    bear = RandomCreature(12, 20, 3, actions = [sword], name = "Bear")

    grid = Grid(6, 6, space = 3)

    monster_pos = [(0,0), (0,1)]
    player_pos = [(5,5), (5,4)]

    game = Game(players = [random1, elmo], monsters = [random2, bear],map =grid, player_pos = player_pos, monster_pos = monster_pos)
    #game.play_game(debug=True)
    game.play_game(debug=True)
