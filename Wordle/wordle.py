from colorama import Fore, Back, Style, init
init(autoreset = True)
from wordle_secret_words import get_secret_words
from valid_wordle_guesses import get_valid_wordle_guesses
import random


def colored_print(feedback):
    '''Prints all guesses formatted to show how correct each letter is based on Wordle schema. 
        
        Args:
         feedback (list): A list of feedback strings, which could be empty
        
    '''
    for word in feedback:
        for char in word:
            if char == '-':
                print(Back.LIGHTBLACK_EX + Fore.WHITE + char, end = "")
            elif char.islower():
                print(Back.YELLOW + Fore.WHITE + char, end = "")
            else:
                print(Back.GREEN + Fore.WHITE + char.upper(), end = "")
        print("\n")

def get_feedback(guess: str, secret_word: str) -> str:
    '''Generates a feedback string based on comparing a 5-letter guess with the secret word. 
       The feedback string uses the following schema: 
        - Correct letter, correct spot: uppercase letter ('A'-'Z')
        - Correct letter, wrong spot: lowercase letter ('a'-'z')
        - Letter not in the word: '-'

        Args:
            guess (str): The guessed word
            secret_word (str): The secret word

        Returns:
            str: Feedback string, based on comparing guess with the secret word
    
        Examples
        >>> get_feedback("lever", "EATEN")
        "-e-E-"
            
        >>> get_feedback("LEVER", "LOWER")
                "L--ER"
            
        >>> get_feedback("MOMMY", "MADAM")
                "M-m--"
            
        >>> get_feedback("ARGUE", "MOTTO")
                "-----"
    
    '''
    guess = guess.upper()
    secret_word = secret_word.upper()
    letters_left = list(guess)
    secret_letters = list(secret_word.upper())
    answer = ["-"] * 5
    for index, letter in enumerate(guess):
        if letter == secret_word[index]:
            answer[index] = letter.upper()
            letters_left[index] = ""
            secret_letters.remove(letter)
    for index, letter in enumerate(letters_left):
        if letter in secret_letters:
            answer[index] = letter.lower()
            secret_letters.remove(letter)

    return "".join(answer)

def get_AI_guess(guesses: list[str], feedback: list[str], valid_guesses: set[str]) -> str:
    '''Analyzes feedback from previous guesses/feedback (if any) to make a new guess
        
        Args:
         guesses (list): A list of string guesses, which could be empty
         feedback (list): A list of feedback strings, which could be empty
         secret_words (set): A set of potential secret words
         valid_guesses (set): A set of valid AI guesses
        
        Returns:
         str: a valid guess that is exactly 5 uppercase letters
    '''
    ai = AI(valid_guesses)
    for index, guess in enumerate(guesses):
        ai.possible_guesses = ai.narrow_down(feedback[index], guess)

    return ai.get_next_guess(len(guesses) + 1)

class AI:
    def __init__(self, valid_guesses):
        self.possible_guesses = valid_guesses
    
    def get_next_guess(self, guess_number):
        '''Predicts the next most optimal guess according to available guesses    
        
            Args:
            guess_number (int): The current guess attempt number
            
            Returns:
            str: a valid guess that is exactly 5 uppercase letters
        '''
        min_guess = 5000
        best_guess = ""

        if guess_number == 1:
            return "ARISE"

        for guess in self.possible_guesses:
            guess_dict = {}
            
            for word in self.possible_guesses:
                result = get_feedback(guess, word)
                guess_dict[result] = guess_dict.get(result, 0) + 1

            max_guess = max(guess_dict.values())
            if max_guess < min_guess:
                min_guess = max_guess
                best_guess = guess

        return best_guess

    def narrow_down(self, result, guess):
        '''Narrows down the number of possible guesses remaining from given guess and result
            
            Args:
            guesses (str): A given guess
            result (str): A result from the given guess
            
            Returns:
            set: a set of remaining possible guesses
        '''
        possible = set()
        for word in self.possible_guesses:
            if get_feedback(guess, word) == result:
                possible.add(word)
        return possible

# Plays Wordle with the option of AI assistance
if __name__ == "__main__":
    secret_word = random.choice(list(get_secret_words()))
    guesses = []
    feedback = []
    turns = 0
    ai = (input("Do you want AI suggestions? (Y)\n")).upper()
    while True:
        if ai == "Y":
            suggestion = get_AI_guess(guesses, feedback, get_valid_wordle_guesses())
            print("AI guess is: " + suggestion)
        guess = input("Input your guess:\n")
        guesses.append(guess)
        result = get_feedback(guess, secret_word)
        feedback.append(result)
        colored_print(feedback)
        if result == secret_word:
             print("Congrats! You won")
             break
        else:
            turns += 1
            if turns == 6:
                print("You Lost! The word was " + secret_word)
                break