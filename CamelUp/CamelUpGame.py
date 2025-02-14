# To install colorama, run the following command in your VS Code terminal:
# python3 -m pip install colorama
from colorama import Fore, Back, Style, init
from CamelUpBoard import CamelUpBoard
from CamelUpPlayer import CamelUpPlayer

class CamelUpGame:
    def __init__(self, p1_name:str, p2_name:str):
        self.CAMEL_STYLES= {
            "r": Back.RED+Style.BRIGHT,
            "b": Back.BLUE+Style.BRIGHT,
            "g": Back.GREEN+Style.BRIGHT,
            "y": Back.YELLOW+Style.BRIGHT,
            "p": Back.MAGENTA
        }
        self.board = CamelUpBoard(self.CAMEL_STYLES)
        self.players = CamelUpPlayer(p1_name), CamelUpPlayer(p2_name)
    
    def get_player_move(self, player: CamelUpPlayer)->str:
        """Prompts the use to enter a valid menu choice:
            - B or b to place a bet
            - R or r to shake the pyramd
        """ 
        print(f"{player.name}-", end = " ")     
        choice = "not_an_option"
        while choice.lower() not in ["b", "r"]:
            choice = input("(B)et or (R)oll? ").lower()
        return choice
    
    def print_AI_Advice(self):
        '''Prints both the enumerative and experimental probability of each camel coming in 
           first or second place for the current leg of the race

           Return
             dict(str, tuple(float, float)) - A dictionary containing the enumerative probabilites for all camels
        '''
        print("  Enumerative\tExperimental")
        enum = self.board.run_enumerative_leg_analysis()
        exper = self.board.run_experimental_leg_analysis(5000)
        analysis = [(self.CAMEL_STYLES[c] + c + Style.RESET_ALL, enum[c][0],enum[c][1], exper[c][0], exper[c][1])  for c in enum ]
        print("   1st   2nd\t 1st   2nd")
        for row in analysis:
            print("{: >1} {: >5.2f} {: >5.2f} \t{: >5.2f} {: >5.2f}".format(*row))
        return enum

    def get_ticket_EV(self, ticket_value:int, prob_first:float, prob_second:float)->float:
        '''Caclulates the Expected Value of a ticket
           
            Args:
                ticket_value (int): The value of a betting ticket if a camel comes in first place for a leg 
                prob_first (float): The probability (0.0 - 1.0) that a camel will come in fist place
                prob_second (float): The probability (0.0 - 1.0) that a camel will come in second place
            
            Return:
                float: The expected value of the ticket
        '''
        ev = ticket_value * prob_first + 1 * prob_second - 1 * (1 - prob_second-prob_first)
        return ev
    
    def get_player_bet(self, player:CamelUpPlayer) -> str:
        '''Prompts a player to select an available betting ticket.
           Also reveals both the enumerative and experimental probabilites of each camel 
           coming in either first or second place, and the expected value of each available betting ticket
        '''
        print("AI Advice-")
        enum = self.print_AI_Advice()

        available_tickets = "Available bets: "
        for color in self.board.ticket_tents:
            tickets_left = self.board.ticket_tents[color]
            if len(tickets_left) > 0:
                top_ticket_value = tickets_left[0]
                ev = self.get_ticket_EV(top_ticket_value, enum[color][0], enum[color][1])
                available_tickets += f"({color})"+self.CAMEL_STYLES[color] + str(top_ticket_value) + Style.RESET_ALL + f" EV:{ev:.2f} "
            else:
                available_tickets += f"({color})"+self.CAMEL_STYLES[color] + "X" + Style.RESET_ALL + " "
        print(available_tickets)
        
        ticket_color = "not_an_option"
        while ticket_color.lower() not in self.CAMEL_STYLES.keys() or len(self.board.ticket_tents[ticket_color]) <= 0:
            ticket_color = input("Which bet would you like to place?\n").lower()

        return ticket_color.lower()

    def play_1_leg(self):
        '''Alternatingly prompts each player to either Bet or Roll until all dice have been 
           placed on Dice Tents
        '''
        curr_player = 0
        while not self.board.is_leg_finished():
            player = self.players[curr_player]
            move = self.get_player_move(player)
            match move:
                case "r":
                    rolled_die = self.board.shake_pyramid()
                    self.board.move_camel(rolled_die)
                    player.win_money(1)
                case "b":
                    ticket_color = self.get_player_bet(player)
                    ticket = self.board.place_bet(ticket_color)
                    player.add_bet(ticket)
            self.board.print(self.players)
            curr_player = (curr_player + 1) % 2
    
    def leg_payouts_and_results(self):
        '''Calculates and displays the final rankings for a race leg.
        '''
        first, second = self.board.get_rankings()
        print(f"{self.CAMEL_STYLES[first]}{first}{Style.RESET_ALL} comes in 1st 🥇🥇🥇!")
        print(f"{self.CAMEL_STYLES[second]}{second}{Style.RESET_ALL} comes in 2nd 🥈🥈🥈!")
        for player in self.players:
            for bet in player.bets:
                if bet[0] == first:
                    player.win_money(bet[1]) # first -> value of card
                elif bet[0] == second:
                    player.win_money(1) # second -> win $1
                else:
                    player.pay_money(1) # second -> lose $1

if __name__ == "__main__":
    camelup = CamelUpGame("p1", "p2")
    camelup.board.print(camelup.players)
    camelup.play_1_leg()
    camelup.leg_payouts_and_results()
    for player in camelup.players:
        print(f"{player.name} ended the leg with {player.money} coins.")