import pygame
import sys
import random
import os

# initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1000, 800 
SCALE_X, SCALE_Y = WIDTH / 800, HEIGHT / 600
CARD_WIDTH = int(WIDTH * 0.1)  # cards take up 10% of the screen width
CARD_HEIGHT = int(HEIGHT * 0.16)  # cards take up 16% of the screen height
font_size = int(24 * SCALE_Y)  # scale font size
font = pygame.font.Font(None, font_size)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solitaire")
clock = pygame.time.Clock()

def load_card_images():
    card_images = {}
    suits = ['S', 'H', 'D', 'C']  # match the suits used in load_deck
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']  # match the ranks used in load_deck
    suit_names = ['spades', 'hearts', 'diamonds', 'clubs']
    rank_names = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']

    for suit, suit_name in zip(suits, suit_names):
        for rank, rank_name in zip(ranks, rank_names):
            filename = os.path.join("cards", f"{rank_name}_of_{suit_name}.png")
            if os.path.exists(filename):
                image = pygame.image.load(filename).convert_alpha()
                card_images[(rank, suit)] = image
            else:
                print(f"Warning: Missing file {filename}")
    return card_images

def load_back_image():
    filename = os.path.join("cards", "back.png")
    if os.path.exists(filename):
        return pygame.image.load(filename).convert_alpha()
    else:
        print("Warning: Missing back image.")
        return None

card_images = load_card_images()
back_image = load_back_image()

class Card:
    def __init__(self, rank, suit, image):
        self.rank = rank
        self.suit = suit
        self.image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
        self.rect = self.image.get_rect()
        self.face_up = False

    def draw(self, surface):
        if self.face_up:
            surface.blit(self.image, self.rect)
        else:
            # draw the back image if the card is face down.
            scaled_back = pygame.transform.scale(back_image, (CARD_WIDTH, CARD_HEIGHT))
            surface.blit(scaled_back, self.rect)

class Solitaire:
    def __init__(self):
        self.deck = []
        self.tableau = [[] for _ in range(7)]   # 7 piles for the tableau
        self.stock = []                         # cards remaining after dealing
        self.waste = []                         # cards flipped from the stock
        self.foundations = [[] for _ in range(4)] # 4 foundation piles
        self.setup_game()
    
    def setup_game(self):
        self.load_deck()
        self.deal_cards()
    
    def load_deck(self):
        # create a full deck of 52 cards.
        suits = ['S', 'H', 'D', 'C']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        for suit in suits:
            for rank in ranks:
                image = card_images.get((rank, suit))
                if image:
                    card = Card(rank, suit, image)
                    self.deck.append(card)
        random.shuffle(self.deck)
    
    def deal_cards(self):
        # deal cards into the tableau: first pile gets 1 card, second gets 2, etc.
        for i in range(7):
            for j in range(i + 1):
                card = self.deck.pop()
                # Only the top card in each column is face up.
                card.face_up = (j == i)
                self.tableau[i].append(card)
        # the remaining cards become the stock.
        self.stock = self.deck.copy()
        self.deck = []  # clear the deck as it's now in use.
        self.waste = []  # Ensure the waste pile is empty.
    
    def draw(self, surface):
        # draw the tableau piles.
        for i, pile in enumerate(self.tableau):
            x = int(50 * SCALE_X + i * (CARD_WIDTH + 20))  # adjust horizontal spacing
            y = int(150 * SCALE_Y)  # adjust vertical starting position
            for j, card in enumerate(pile):
                card.rect.topleft = (x, y + int(j * (CARD_HEIGHT * 0.3)))  # adjust vertical spacing
                card.draw(surface)

        # draw the stock (if available).
        if self.stock:
            stock_rect = pygame.Rect(
                int(50 * SCALE_X), int(50 * SCALE_Y),
                CARD_WIDTH, CARD_HEIGHT
            )
            surface.blit(pygame.transform.scale(back_image, stock_rect.size), stock_rect)
        else:
            # if no stock, draw an empty placeholder.
            pygame.draw.rect(
                surface, (200, 200, 200),
                (int(50 * SCALE_X), int(50 * SCALE_Y), CARD_WIDTH, CARD_HEIGHT)
            )

        # draw the waste pile (showing only the top card).
        if self.waste:
            waste_card = self.waste[-1]
            waste_card.rect.topleft = (int(170 * SCALE_X), int(50 * SCALE_Y))
            waste_card.face_up = True
            waste_card.draw(surface)

        # draw the foundation piles.
        for i, foundation in enumerate(self.foundations):
            x = int(400 * SCALE_X + i * (CARD_WIDTH + 20))  # adjust horizontal spacing for foundations
            y = int(50 * SCALE_Y)  # position foundations at the top
            if foundation:
                top_card = foundation[-1]
                top_card.rect.topleft = (x, y)
                top_card.draw(surface)
            else:
                # draw an empty placeholder for the foundation.
                pygame.draw.rect(
                    surface, (200, 200, 200),
                    (x, y, CARD_WIDTH, CARD_HEIGHT)
                )
    
    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                # check if the stock pile was clicked.
                stock_rect = pygame.Rect(
                    int(50 * SCALE_X), int(50 * SCALE_Y),
                    CARD_WIDTH, CARD_HEIGHT
                )
                if stock_rect.collidepoint(pos):
                    if self.stock:  # if the stock is not empty.
                        card = self.stock.pop()
                        card.face_up = True
                        self.waste.append(card)
                    elif self.waste:  # if the stock is empty, reset it from the waste pile.
                        self.stock = self.waste[::-1]  # reverse the waste pile.
                        for card in self.stock:
                            card.face_up = False
                        self.waste = []
                    return  # stop processing once the stock pile is handled.

                # check if a card in the tableau was clicked.
                for i, pile in enumerate(self.tableau):
                    for j, card in enumerate(pile):
                        if card.rect.collidepoint(pos) and card.face_up:
                            # attempt to move the card to a foundation or another tableau pile.
                            if self.move_to_foundation(card, i, j) or self.move_to_tableau(card, i, j):
                                return  # stop processing once a move is made.

                # check if the waste pile was clicked.
                if self.waste and self.waste[-1].rect.collidepoint(pos):
                    card = self.waste[-1]
                    # attempt to move the card to a foundation or tableau pile.
                    if self.move_to_foundation(card, from_waste=True) or self.move_to_tableau(card, from_waste=True):
                        return  # stop processing once a move is made.

    def move_to_foundation(self, card, tableau_index=None, card_index=None, from_waste=False):
        for foundation in self.foundations:
            if not foundation:
                # if the foundation is empty, only an Ace can be placed.
                if card.rank == 'A':
                    self._move_card_to_foundation(card, foundation, tableau_index, card_index, from_waste)
                    return True
            else:
                top_card = foundation[-1]
                # check if the card is the next in sequence and of the same suit.
                if top_card.suit == card.suit and self._is_next_rank(top_card.rank, card.rank):
                    self._move_card_to_foundation(card, foundation, tableau_index, card_index, from_waste)
                    return True
        return False

    def move_to_tableau(self, card, tableau_index=None, card_index=None, from_waste=False):
        for i, pile in enumerate(self.tableau):
            if not from_waste and i == tableau_index:
                continue  # skip the pile the card is already in.
            if not pile:
                # if the pile is empty, only a King can be placed.
                if card.rank == 'K':
                    if from_waste:
                        self._move_card_to_tableau(card, pile, None, None, from_waste)
                    else:
                        self._move_cards_to_tableau(self.tableau[tableau_index][card_index:], pile, tableau_index)
                    return True
            else:
                top_card = pile[-1]
                # check if the card is the opposite color and one rank lower.
                if self._is_opposite_color(top_card.suit, card.suit) and self._is_next_rank(card.rank, top_card.rank):
                    if from_waste:
                        self._move_card_to_tableau(card, pile, None, None, from_waste)
                    else:
                        self._move_cards_to_tableau(self.tableau[tableau_index][card_index:], pile, tableau_index)
                    return True
        return False

    def _move_cards_to_tableau(self, cards, pile, tableau_index):
        pile.extend(cards)
        self.tableau[tableau_index] = self.tableau[tableau_index][:-len(cards)]
        if self.tableau[tableau_index]:
            self.tableau[tableau_index][-1].face_up = True

    def _move_card_to_foundation(self, card, foundation, tableau_index, card_index, from_waste):
        foundation.append(card)  # add the card to the foundation.
        if from_waste:
            self.waste.pop()  # remove the card from the waste pile.
        else:
            # remove the card from its original tableau pile.
            self.tableau[tableau_index].pop(card_index)
            # Flip the card below (if any) face up.
            if self.tableau[tableau_index]:
                self.tableau[tableau_index][-1].face_up = True

    def _move_card_to_tableau(self, card, pile, tableau_index, card_index, from_waste):
        pile.append(card)
        if from_waste:
            self.waste.pop()
        else:
            # remove the card from its original tableau pile.
            self.tableau[tableau_index] = self.tableau[tableau_index][:card_index]
            # Flip the card below (if any) face up.
            if self.tableau[tableau_index]:
                self.tableau[tableau_index][-1].face_up = True

    def _is_next_rank(self, rank1, rank2):
        # define the order of ranks.
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        return ranks.index(rank2) == ranks.index(rank1) + 1

    def _is_opposite_color(self, suit1, suit2):
        # define suits by color.
        red_suits = ['H', 'D']
        black_suits = ['S', 'C']
        return (suit1 in red_suits and suit2 in black_suits) or (suit1 in black_suits and suit2 in red_suits)
    
    def check_win(self):
    # the game is won if all foundation piles contain 13 cards (A to K).
        return all(len(foundation) == 13 for foundation in self.foundations)

def main():
    game = Solitaire()
    running = True
    while running:
        if game.check_win():
            print("You win!")
            running = False
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        game.update(events)
        screen.fill((0, 128, 0))
        game.draw(screen)
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
