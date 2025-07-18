from rest_framework import serializers
from .models import User, Game, Move

# PUBLIC_INTERFACE
class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'created_at']

# PUBLIC_INTERFACE
class MoveSerializer(serializers.ModelSerializer):
    """Serializer for the Move model."""
    player = UserSerializer(read_only=True)
    class Meta:
        model = Move
        fields = ['id', 'player', 'position', 'turn', 'played_at']

# PUBLIC_INTERFACE
class GameSerializer(serializers.ModelSerializer):
    """Serializer for the Game model."""
    player_x = UserSerializer(read_only=True)
    player_o = UserSerializer(read_only=True)
    winner = UserSerializer(read_only=True)
    moves = MoveSerializer(many=True, read_only=True)
    class Meta:
        model = Game
        fields = [
            'id', 'player_x', 'player_o', 'current_turn', 'status',
            'winner', 'board', 'created_at', 'moves'
        ]

# Simple scoreboard serializer (aggregate, no model)
class ScoreboardSerializer(serializers.Serializer):
    username = serializers.CharField()
    wins = serializers.IntegerField()
    losses = serializers.IntegerField()
    draws = serializers.IntegerField()
