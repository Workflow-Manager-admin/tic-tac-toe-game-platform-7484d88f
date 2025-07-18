from django.db import models

# PUBLIC_INTERFACE
class User(models.Model):
    """Represents a player in the game."""
    username = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

GAME_STATUS_CHOICES = [
    ("IN_PROGRESS", "In Progress"),
    ("FINISHED", "Finished"),
]

# PUBLIC_INTERFACE
class Game(models.Model):
    """Represents a Tic Tac Toe game."""
    player_x = models.ForeignKey(User, related_name="games_as_x", on_delete=models.CASCADE)
    player_o = models.ForeignKey(User, related_name="games_as_o", on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=GAME_STATUS_CHOICES, default="IN_PROGRESS")
    winner = models.ForeignKey(User, related_name="games_won", null=True, blank=True, on_delete=models.SET_NULL)
    current_turn = models.CharField(max_length=1, choices=(("X", "X"), ("O", "O")), default="X")
    created_at = models.DateTimeField(auto_now_add=True)
    board = models.CharField(max_length=9, default=" " * 9)  # Linearized board, length 9

    def __str__(self):
        return f"Game {self.id} ({self.player_x} vs {self.player_o})"

    def display_board(self):
        """Returns the board as a 2D list."""
        return [list(self.board[i*3:(i+1)*3]) for i in range(3)]

    def make_move(self, user, position):
        """
        Apply a move; position is an integer 0-8.
        Returns True if move applied, raises ValueError if not valid.
        """
        if self.status != "IN_PROGRESS":
            raise ValueError("Game is finished.")

        if self.current_turn == "X" and user != self.player_x:
            raise ValueError("It's not your turn.")
        if self.current_turn == "O" and user != self.player_o:
            raise ValueError("It's not your turn.")
        if not (0 <= position <= 8) or self.board[position] != " ":
            raise ValueError("Invalid position.")
        board = list(self.board)
        board[position] = self.current_turn
        self.board = "".join(board)
        Move.objects.create(game=self, player=user, position=position, turn=self.current_turn)
        # Check victory
        win = self.check_winner()
        if win:
            self.status = "FINISHED"
            self.winner = user
        elif " " not in self.board:  # Draw
            self.status = "FINISHED"
            self.winner = None
        else:
            self.current_turn = "O" if self.current_turn == "X" else "X"
        self.save()
        return True

    def check_winner(self):
        """Check the board for a winner; returns True if win."""
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # cols
            [0, 4, 8], [2, 4, 6],             # diagonals
        ]
        for line in lines:
            a, b, c = line
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] != " ":
                return True
        return False

# PUBLIC_INTERFACE
class Move(models.Model):
    """A move in a game."""
    game = models.ForeignKey(Game, related_name="moves", on_delete=models.CASCADE)
    player = models.ForeignKey(User, related_name="moves", on_delete=models.CASCADE)
    position = models.PositiveIntegerField()  # 0-8
    turn = models.CharField(max_length=1, choices=(("X", "X"), ("O", "O")))
    played_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.turn}] {self.player.username} at {self.position} (game {self.game.id})"
