# To install colorama, run the following command in your VS Code terminal:
# python3 -m pip install colorama
from colorama import Fore, Back, Style, init

class CamelUpPlayer:
    def __init__(self, name:str):
        self.money = 3 # Camel Up players start with 3 coins
        self.bets = [] 
        self.name = name
    
    def win_money(self, amount:int):
        self.money += amount
    
    def pay_money(self, amount:int):
        self.money -= amount
    
    def add_bet(self, ticket:tuple[str, int]):
        self.bets.append(ticket)
    
    def reset_tickets(self):
        self.bets = []
    
if __name__ == "__main__":
    player = CamelUpPlayer("test")
    player.add_bet(('y, 5'))
    