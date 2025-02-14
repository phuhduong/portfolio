from colorama import Fore, Back, Style, init
from itertools import permutations, product
from CamelUpPlayer import CamelUpPlayer
import random
import copy 


class CamelUpBoard:
    def __init__(self, camel_styles: list[str]):
        self.TRACK_POSITIONS = 16
        self.DICE_VALUES = [1,2,3]
        self.BETTING_TICKET_VALUES = [5, 3, 2, 2]

        self.camel_styles = camel_styles
        self.camel_colors = camel_styles.keys()
        self.track = self.starting_camel_positions()
        self.pyramid = set(self.camel_colors)
        self.ticket_tents = {color:self.BETTING_TICKET_VALUES.copy() for color in self.camel_colors}
        self.dice_tents = [] # preserves order

    def starting_camel_positions(self) -> list[list[str]]:
        '''Places camels on the board at the beginning of the game
            TODO: randomize these positions

            Return
               list[list[str]] - a 2D list model of the Camel Up race track
        '''
        track = [[] for i in range(self.TRACK_POSITIONS)]
        track[0] = list(self.camel_colors)
        random.shuffle(track[0])
        for camel in range(4, -1, -1):
            start_pos = random.randint(1, 3)
            track[start_pos].append(track[0].pop(camel))
        return track

    def print(self, players: list[CamelUpPlayer]):
        '''Prints the current state of the Camel Up board, including:
            - Race track with current camel positions
            - Betting Tents displaying available betting tickets
            - Dice Tents displaying an ordered collection of rolled dice
            - Player information for both players
                - name
                - coins
                - betting tickets for the current leg of the race
        '''
        board_string = "\n"

         # Ticket Tents
        ticket_string = "Ticket Tents: "
        for ticket_color in self.ticket_tents:
            if len(self.ticket_tents[ticket_color]) > 0:
                next_ticket_value = str(self.ticket_tents[ticket_color][0])
            else:
                next_ticket_value = 'X'
            ticket_string += self.camel_styles[ticket_color] + next_ticket_value+Style.RESET_ALL + " "
        board_string += ticket_string + "\t\t"

        # Dice Tents
        dice_string = "Dice Tents: "
        for die in self.dice_tents:
            dice_string += self.camel_styles[die[0]] + str(die[1]) + Style.RESET_ALL + " "
        for i in range (5 - len(self.dice_tents)):
            dice_string += Back.WHITE + " " + Style.RESET_ALL + " "
        
        # Camels and Race Track
        board_string += dice_string +"\n"
        for row in range(4, -1, -1):
            row_str = [" "] * 16
            for i in range(len(self.track)):
                for camel_place, camel in enumerate(self.track[i]):
                    if camel_place == row:
                        row_str[i] = self.camel_styles[camel] + camel + Style.RESET_ALL 
            board_string += "🌴 " + str("   ".join(row_str)) + " |🏁\n"
        board_string += "   " + "".join([str(i) + "   " for i in range(1, 10)])
        board_string += "".join([str(i) + "  " for i in range(10, 17)]) + "\n"

        #Player Info
        player_string = ""
        for player in players:
            player_string += f"{player.name} has {player.money} coins."
            if len(player.bets) > 0:
                bets_string = " ".join([self.camel_styles[bet[0]] + str(bet[1]) + Style.RESET_ALL for bet in player.bets])
                player_string += f" Bets: {bets_string}"  
            player_string += "\t\t" 
        board_string += player_string
        print(board_string + "\n")

    def reset_tents(self):
        '''Rests dice tents and ticket tents at the end of a leg
        '''
        self.ticket_tents = {color:self.BETTING_TICKET_VALUES.copy() for color in self.camel_colors}
        self.dice_tents = []

    def place_bet(self, color:str) -> tuple[str, int]:
        '''Manages the board perspective when a player places a bet:
            - removes the top betting ticket (with highest value) from the appropriate Ticket Tent
            - returns the ticket

            Args
               color (str) - the color of the ticket on which a player would like to bet: 'r'
           
            Return
                tuple(str, int) - a tuple representation of a betting ticket: ('r', 5)
        '''
        tickets_left = self.ticket_tents[color]
        ticket = ()
        if len(tickets_left) > 0:
            ticket = (color, tickets_left[0])
            self.ticket_tents[color] = tickets_left[1:]
        return ticket
    
    def get_camel_position(self, color: str) -> tuple:
        for row in range(len(self.track)):
            for col in range(len(self.track[row])):
                if color ==  self.track[row][col]:
                    return tuple((row, col))

    def move_camel(self, die:tuple[str, int], verbose = False):
        '''Updates the track according to the die color and value
           The camel of the appropriate color moves the apporpriate number of spaces, 
           along with all camels riding on top of that camel.

           Args
             die (tuple[str, int]) - A tuple represntation of the die: ('g', 2)

           Return
             list[list[str]] - a 2D list model of the Camel Up race track
        '''
        if verbose: print("Current track state:", self.track)
        color, step = die
        row, col = self.get_camel_position(color)
        new_row = row + step
        camels = self.track[row][col:]
        for camel in camels:
            self.track[new_row].append(camel)
        del self.track[row][col:] 
        if verbose: print("Updated track state:", self.track)
        return self.track
    
    def shake_pyramid(self) -> tuple[str, int]:
        '''Manages all the steps (from the board persepctive) involved with shaking the pyramid, 
           which includes:
                - selecting a random color and dice value from the dice colors in the pyramid
                - removing the rolled dice from the pyramid
                - placing the rolled dice in the dice tents

            Return
                tuple[str, int] - A tuple representation of the rolled die
        '''        
        if len(self.pyramid) == 0:
            return tuple(['', 0])
        val = random.choice(self.DICE_VALUES)
        color = random.choice(list(self.pyramid))
        rolled_die = tuple([color, val])
        self.pyramid.remove(color)
        self.dice_tents.append(rolled_die)
        return rolled_die

    def is_leg_finished(self) -> bool:
        '''Determines whether the leg of a race is finished

           Return
             bool - True if all dice have been rolled, False otherwise
        '''
        return len(self.dice_tents) == 5

    def get_rankings(self):
        '''Determines first and second place camels on the track
           
           Returns:
            tuple: a tuple of strings of (1st, 2nd) place camels: ('b', 'y') 
        '''
        rankings = []
        for position in range(len(self.track) - 1, -1, -1):
            for camel in reversed(self.track[position]):
                rankings.append(camel)
        return tuple([rankings[0], rankings[1]])

    def get_all_dice_roll_sequences(self)-> set:
        '''
            Constructs a set of all possible roll sequences for the dice currently in the pyramid
            Note: Use itertools product function

            Return
               set[tuple[tuple[str, int]]] - A set of tuples representing all the ordered dice seqences 
                                             that could result from shaking all dice from the pyramid
        ''' 
        all_color_seq = permutations(self.pyramid)
        roll_space = set()
        all_num_seq = product(self.DICE_VALUES, repeat = len(self.pyramid))
        current = set(product(all_color_seq, all_num_seq))
        for sequence in current:
            rolls = []
            for i in range(len(sequence[0])):
                rolls.append(tuple([sequence[0][i], sequence[1][i]]))
            roll_space.add(tuple(rolls))
        return roll_space
    
    def run_enumerative_leg_analysis(self)->dict[str, tuple[float, float]]:
        '''Conducts an enumerative analysis of the probability that each camel will win either 1st or 
           2nd place in this leg of the race. The enumerative analysis counts 1st/2nd place finishes 
           via calculating the entire state space tree

           General Steps:
                1) Precalculate all possible dice sequences for the dice currently in the pyramid
                2) Move through each sequence of possible dice rolls to count the number of 1st/2nd places 
                   finishes for each camel
                3) Calculates the probability that each camel will come in 1st or 2nd based on the total 
                   number of 1st/2nd finishes out of the total number of dice sequences

                TODO: Add notes about using deepcopy to preserve state
           
           Returns: 
              dict[str, tuple[float, float]] - A dictionary representing the probabilities that a camel will 
                                               come in first or second place according to an enumerative analysis
                {
                    'r':(0.5, 0.2),
                    'b':(0.1, 0.04),
                    ...
                }
        '''
        first_place = {color: 0 for color in self.camel_colors}
        second_place = {color: 0 for color in self.camel_colors}
        roll_space = self.get_all_dice_roll_sequences()
        
        current_track = copy.deepcopy(self.track)
        for roll_sequence in roll_space:
            for roll in roll_sequence:
                self.move_camel(roll)
            top_two = self.get_rankings()
            first_place[top_two[0]] += 1
            second_place[top_two[1]] += 1
            del self.track[:]
            self.track = copy.deepcopy(current_track)
        
        total_counts = max(len(roll_space), 1)
        win_percents = {color:(float(round(first_place[color] / total_counts, 3)), 
                             float(round(second_place[color] / total_counts, 3))) for color in self.camel_colors}
        return win_percents

    def run_experimental_leg_analysis(self, trials:int)->dict[str, tuple[float, float]]:
        '''Conducts an experimental analysis (ie. a random simulation) of the probability that each camel
            will win either 1st or 2nd place in this leg of the race. The experimenta analysis counts 
            1st/2nd place finishes bycounting outcomes from randomly shaking the pyramid over a given 
            number of trials.
           
           General Steps:
                1) Shake the pyramid enough times to randomly generate a dice sequence to finish the leg
                2) Count a 1st/2nd place finish for each camel
                3) Repeat steps #1 - #2 trials number of times
                3) Calculate the probability that each camel will come in 1st or 2nd based on the total 
                   number of 1st/2nd finishes out of the total number of trials

                TODO: Add notes about using deepcopy to preserve state

           Args
              trials (int): The number of random simulations to conduct

           Returns: 
              dict[str, tuple[float, float]] - A dictionary representing the probabilities that a camel will 
                                               come in first or second place according to an enumerative analysis
                {
                    'r':(0.5, 0.2),
                    'b':(0.1, 0.04),
                    ...
                }
        '''
        first_place = {color: 0 for color in self.camel_colors}
        second_place = {color: 0 for color in self.camel_colors}

        for trial in range(trials):
            current_track = copy.deepcopy(self.track)
            current_pyramid = copy.deepcopy(self.pyramid)
            current_dice_tent = copy.deepcopy(self.dice_tents)

            while self.pyramid:
                roll = self.shake_pyramid()
                self.move_camel(roll)

            top_two = self.get_rankings()
            first_place[top_two[0]] += 1
            second_place[top_two[1]] += 1
            del self.dice_tents, self.track, self.pyramid
            self.dice_tents = current_dice_tent
            self.track = current_track
            self.pyramid = current_pyramid        

        win_percents = {color:(float(round(first_place[color] / trials, 3)), 
                             float(round(second_place[color] / trials, 3))) for color in self.camel_colors}
        return win_percents
   
if __name__ == "__main__":
    camel_styles= {
            "r": Back.RED+Style.BRIGHT,
            "b": Back.BLUE+Style.BRIGHT,
            "g": Back.GREEN+Style.BRIGHT,
            "y": Back.YELLOW+Style.BRIGHT,
            "p": Back.MAGENTA
    }

    board = CamelUpBoard(camel_styles)
    p1 = CamelUpPlayer("p1")
    p2 = CamelUpPlayer("p2")
    board.print([p1, p2])
    die = ('b', 1)
    board.move_camel(die)

    # Roll 3 random dice
    rolled_die = board.shake_pyramid()
    board.move_camel(rolled_die)
    rolled_die = board.shake_pyramid()
    board.move_camel(rolled_die)
    rolled_die = board.shake_pyramid()
    board.move_camel(rolled_die)
    board.print([p1, p2])

    # Probabilites
    all_possible_dice_sequences = board.get_all_dice_roll_sequences()
    print(f"{len(all_possible_dice_sequences)} possible dice sequences for {len(board.pyramid)} dice in the pyramid:") 
    print("Enumerative Probabilities:", board.run_enumerative_leg_analysis())
    print("Experimental Probabilities:", board.run_experimental_leg_analysis(5000))
