import pygame
import sys
import cell
from backend.player import AIPlayer, HumanPlayer
from backend.board import ReversiBoard
from main_menu import MainMenu
from front_board import Board

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

### GameUI Class ###
class GameUI:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Initialize reversi engine
        self.reversi = ReversiBoard()

        # Set up the display
        self.ASPECT_RATIO = (8,10)

        # Initial size of the board & game window
        self.screen_width = 480
        self.screen_height = int(self.screen_width / self.ASPECT_RATIO[0] * self.ASPECT_RATIO[1])
        self.square_size = self.screen_width // 8
        self.board_size = self.screen_width
        self.statusbar_height = 2 * self.square_size
        self.statusbar_width = self.screen_width
        

        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        # Set up the board
        self.board = Board()
        self.board.set_valid_moves(self.reversi.getValidMoves('B'))

        # Set up the status bar
        self.statusbar = pygame.Surface(
            (self.statusbar_width, self.statusbar_height))
        self.statusbar.fill(pygame.Color('gray'))

        # Default game mode
        self.game_mode = "VS Player"
        self.difficulty = "easy"

    def update_screen_dimensions(self, width, height):
        self.screen_width = width
        self.screen_height = int(self.screen_width / self.ASPECT_RATIO[0] * self.ASPECT_RATIO[1])
        self.square_size = self.screen_width // 8
        self.board_size = self.screen_width
        self.statusbar_height = 2 * self.square_size
        self.statusbar_width = self.screen_width

    
    def statusbar_message(self, the_turn = "W", white_score = 2, black_score = 2):
        names = {"W": "White", "B": "Black", "Draw": "Draw"}
        font = pygame.font.Font(None, int(23 * self.statusbar_height // 120 ))
        if not self.reversi.isGameOver():
            message = font.render(
                f"{names[the_turn]}'s turn | White: {white_score} | Black: {black_score}", True, BLACK)
        else:
            
            message = font.render(
                f"{names[self.reversi.getWinner()]} wins! | White: {white_score} | Black: {black_score}", True, BLACK)
            
        message_rect = message.get_rect(
            center=(self.statusbar_width // 2, self.statusbar_height // 2))
        self.statusbar.fill(pygame.Color('gray'))
        self.statusbar.blit(message, message_rect)

        # add a botton in most top left corner
        home_button = pygame.Rect(0, 0, self.square_size, self.square_size)
        pygame.draw.rect(self.statusbar, pygame.Color('green'), home_button)
        home_button_text = font.render("Home", True, BLACK)
        home_button_text_rect = home_button_text.get_rect(
            center=(home_button.width // 2, home_button.height // 2))
        # Add stroke to the rectangle
        pygame.draw.rect(self.statusbar, BLACK, home_button, 1)
        self.statusbar.blit(home_button_text, home_button_text_rect)

        restart_button = pygame.Rect(0, self.square_size, self.square_size, self.square_size)
        pygame.draw.rect(self.statusbar, pygame.Color('orange'), restart_button)
        restart_button_text = font.render("Restart", True, BLACK)
        restart_button_text_rect = restart_button_text.get_rect(
            center=((restart_button.width // 2), (restart_button.height // 2) + self.square_size))
        pygame.draw.rect(self.statusbar, BLACK, restart_button, 1)
        self.statusbar.blit(restart_button_text, restart_button_text_rect)

        # add a botton in most top right corner
        # pygame.draw.rect(self.statusbar, WHITE, (0, 0, self.statusbar_width, self.statusbar_height), 2)

    def set_game_mode(self, value, game_mode):
        self.game_mode = game_mode

    def set_difficulty(self, value, difficulty):
        self.difficulty = difficulty

    # Drawing the board
    def draw_board(self):
        for row in range(8):
            for col in range(8):
                new_cell = cell.Cell(row, col, self.board.get_piece(row, col))
                new_cell.draw(self.screen, self.square_size)

    def update_ingame_dimensions(self, event):
        # Update the window dimensions while maintaining the aspect ratio
        window_width = event.w
        window_width = round(window_width / 8) * 8
        window_height = int(window_width / self.ASPECT_RATIO[0] * self.ASPECT_RATIO[1])
        
        self.screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
        self.update_screen_dimensions(window_width, window_height)
        self.draw_board()
        self.statusbar = pygame.Surface(
            (self.statusbar_width, self.statusbar_height))
        self.statusbar.fill(pygame.Color('gray'))

    def handle_mouse_click(self, event):
        x, y = event.pos
        col = x // self.square_size
        row = y // self.square_size
        if not(0 <= row < 8 and 0 <= col < 8):
            print("Invalid move")
        elif self.board.get_piece(row, col) == 'V':
            Board.BOARD[row][col] = self.current_player
            # sending the move to the reversi engine
            self.reversi.makeMove(self.current_player, row, col)

        self.current_player = self.reversi.whoseTurn
        # checking the buttons
        if (row == 8) and (col == 0):
            # home button
            self.start()

        if (row == 9) and (col == 0):
            # restart button
            self.start_game()

        # Updating the whole board
        self.board.set_board(self.reversi.getBoard())
        if self.reversi.whoseTurn == 'W' or self.reversi.whoseTurn == 'B':
            self.board.set_valid_moves(self.reversi.getValidMoves(self.current_player))
        self.draw_board()

    # The main PVP game loop
    def run_pvp(self):
        # game loop
        while True:

            if(self.reversi.isGameOver()):
                self.statusbar_message()

            # show the status bar
            self.screen.blit(
                self.statusbar, (0, self.screen_height - self.statusbar_height))
            self.statusbar_message(self.current_player, self.reversi.getScore('W'), self.reversi.getScore('B'))
            
            # update the display
            pygame.display.flip()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE:
                    self.update_ingame_dimensions(event)

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_mouse_click(event)
            
            self.clock.tick(60)

    # the main PVA game loop
    def run_pva(self):
        # game loop
        while True:
            # show the status bar
            self.screen.blit(
                self.statusbar, (0, self.screen_height - self.statusbar_height))
            self.statusbar_message(self.current_player, self.player2.get_score(), self.player1.get_score())
            
            # update the display
            pygame.display.flip()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE:
                    self.update_ingame_dimensions(event)

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pass


    # the main AVA game loop
    def run_ava(self):
        pass

    def start(self):
        # Update the screen
        pygame.display.set_caption("Othello")
        main_menu = MainMenu(self)
        main_menu.show_welcome_screen()

    def create_player(self, color, player_type):
        """Factory method to create a player object based on the given color and player type."""
        if player_type == 'human':
            return HumanPlayer(color,self.reversi)
        elif player_type == 'ai':
            return AIPlayer(color)

    def start_game(self):
        """Starts the game with the selected game mode and players."""
        self.reversi.restart()
        self.board.reset_board()
        self.board.set_valid_moves(self.reversi.getValidMoves('B'))
        self.draw_board()
        pygame.display.flip()

        # Set current player to Black
        self.current_player = 'B'

        # Create players based on game mode using the factory method
        if self.game_mode == 'VS Player':
            self.player1 = self.create_player('B', 'human')
            self.player2 = self.create_player('W', 'human')
            self.run_pvp()
        elif self.game_mode == 'VS AI':
            self.player1 = self.create_player('B', 'human')
            self.player2 = self.create_player('W', 'ai')
            self.run_pva()
        else:
            self.player1 = self.create_player('B', 'ai')
            self.player2 = self.create_player('W', 'ai')
            self.run_ava()

        # Quit Pygame
        pygame.quit()


if __name__ == '__main__':
    game = GameUI()
    game.start()
