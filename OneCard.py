import random
from abc import ABC, abstractmethod

import self

SUITS = ["Heart", "Diamond", "Spade", "Club"]
RANKS = [2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King", "Ace"]
AT_CARDS = {2: 2, "Ace": 3, "Joker": 5}
SKIP_CARDS = {"Jack", "Queen", "King"}

class GameState:
    deck = None
    user_hand = None
    opponent_hand = None
    opponent_turn_finished = False

class Card(object):
    def __init__(self, suit, rank, abilities=None):
        self.suit = suit
        self.rank = rank
        self.abilities = abilities or []  # Store multiple abilities

    def __str__(self):
        abilities_str = ', '.join(ability.__name__ for ability in self.abilities)
        return f"{self.rank} of {self.suit} ({'Abilities: ' + abilities_str if self.abilities else 'No Ability'})"

class Player(ABC):
    @abstractmethod
    def addInitialCard(self, deck, num):
        pass

    @abstractmethod
    def dropCard(self, card, usedDeck):
        pass

    @abstractmethod
    def takeCard(self, deck):
        pass

class CardAbility:
    def __init__(self, deck, user_hand, opponent_hand):
        self.deck = deck
        self.user_hand = user_hand
        self.opponent_hand = opponent_hand

    def attack(self):
        """Handles attack logic where the opponent draws cards."""
        if self.user_hand in AT_CARDS:
            for _ in range(AT_CARDS[self.user_hand]):
                while not GameState.opponent_turn_finished:
                    pass  # Wait until opponent's turn is finished
                GameState.opponent_turn_finished = False  # Reset for the next turn
                if self.deck.cards:
                    self.opponent_hand.cards.append(self.deck.cards.pop())
            print(f"Opponent draws {AT_CARDS[self.user_hand]} cards!")

    def defence(self, used_deck):
        """Handles defense logic where the user or opponent responds to an attack."""
        if used_deck in AT_CARDS:
            attack_value = AT_CARDS[used_deck]
            while True:
                # Check if the opponent can defend with a valid card
                if self.opponent_hand.cards:
                    defense_card = self.opponent_hand.cards.pop()
                    defense_value = AT_CARDS.get(defense_card, 0)

                    if defense_value >= attack_value:
                        print(f"Opponent defends with {defense_card} (value: {defense_value}).")
                        total_value = attack_value + defense_value
                        print(f"Passing attack value {total_value} to the user.")
                        self.defence(total_value)  # Recursively handle defence
                        break
                    else:
                        print(f"{defense_card} is not a valid defense! Opponent must draw {attack_value} cards.")
                        for _ in range(attack_value):
                            if self.deck.cards:
                                self.opponent_hand.cards.append(self.deck.cards.pop())
                        print("Opponent failed to defend and draws the cards.")
                        break
                else:
                    print(f"Opponent has no cards to defend! They must draw {attack_value} cards.")
                    for _ in range(attack_value):
                        if self.deck.cards:
                            self.opponent_hand.cards.append(self.deck.cards.pop())
                    break

    def change(self, new_suit):
        """7: Change suits for the next turn."""
        print(f"The suit has been changed to {new_suit}.")
        self.deck.suit = new_suit

    def skip(self):
        """Jack, Queen, King: Skip next player's turn."""
        if self.user_hand in SKIP_CARDS:
            GameState.opponent_turn_finished = True
            print("Next player's turn is skipped!")

class Deck(object):
    def __init__(self):
        self.cards = []

        # Define abilities for specific card ranks
        abilities = {
            2: [CardAbility.attack, CardAbility.defence],
            "Ace": [CardAbility.attack, CardAbility.defence],
            "Joker": [CardAbility.attack, CardAbility.defence],
            "Jack": [CardAbility.skip],
            "Queen": [CardAbility.skip],
            "King": [CardAbility.skip],
            7: [CardAbility.change]
        }

        # Generate the deck (52 cards)
        for suit in SUITS:
            for rank in RANKS:
                ability = abilities.get(rank, [])  # Assign ability if it exists
                self.cards.append(Card(suit, rank, ability))

        # Add Jokers with special abilities
        self.cards.append(Card(None, "Joker 1", [CardAbility.attack, CardAbility.defence]))
        self.cards.append(Card(None, "Joker 2", [CardAbility.attack, CardAbility.defence]))

    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self.cards)

    def __repr__(self):
        return f"Deck with {len(self.cards)} cards"


class UsedDeck(object):
    def __init__(self):
        self.cards = []

    def addCard(self, card):
        self.cards.append(card)

    def insertCardsIntoDeck(self, deck):
        random.shuffle(self.cards)

        for card in self.cards:
            deck.addCard(self.cards)

        self.cards.clear()

class HumanDeck(Player):
    def __init__(self):
        self.cards = []

    def addInitialCard(self, deck, num=7):
        """Add a specified number of cards from the Deck to HumanDeck."""
        for _ in range(num):
            if deck.cards:  # Ensure the deck is not empty
                self.cards.append(deck.cards.pop())
            else:
                print("No more cards in the deck to draw!")

    def dropCard(self, card, usedDeck):
        """Drop a card from HumanDeck to the UsedDeck."""
        if card in self.cards:
            self.cards.remove(card)
            usedDeck.cards.append(card)
        else:
            print(f"Card {card} is not in your hand!")

    def takeCard(self, deck):
        """Take a card from the Deck."""
        if deck.cards:
            self.cards.append(deck.cards.pop())
        else:
            print("No more cards in the deck to draw!")

class AIDeck(Player):
    def __init__(self):
        self.cards = []

    def addInitialCard(self, deck, num=7):
        """Add a specified number of cards from the Deck to AIDeck."""
        for _ in range(num):
            self.cards.append(deck.cards.pop())

    def dropCard(self, card, usedDeck):
        """Drop a card from AIDeck to the UsedDeck."""
        self.cards.remove(card)
        usedDeck.cards.append(card)

    def takeCard(self, deck):
        """Take a card from the Deck."""
        self.cards.append(deck.cards.pop())