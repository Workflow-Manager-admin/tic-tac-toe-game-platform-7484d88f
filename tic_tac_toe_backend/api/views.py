from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User, Game
from .serializers import UserSerializer, GameSerializer, ScoreboardSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q

@api_view(['GET'])
def health(request):
    """Health check endpoint."""
    return Response({"message": "Server is up!"})

# PUBLIC_INTERFACE
@api_view(['GET', 'POST'])
def users_list_create(request):
    """
    GET: List all users.
    POST: Create a new user with username.
    """
    if request.method == 'GET':
        users = User.objects.all().order_by('id')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# PUBLIC_INTERFACE
@api_view(['GET', 'POST'])
def games_list_create(request):
    """
    GET: List all games and their state.
    POST: Start a new game with player_x and player_o IDs.
    """
    if request.method == 'GET':
        games = Game.objects.all().order_by('-created_at')
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        x_id = request.data.get('player_x')
        o_id = request.data.get('player_o')
        if not x_id or not o_id or x_id == o_id:
            return Response({'error': 'Need distinct player_x and player_o IDs.'}, status=400)
        try:
            player_x = User.objects.get(id=x_id)
            player_o = User.objects.get(id=o_id)
        except User.DoesNotExist:
            return Response({'error': 'Both players must exist.'}, status=400)
        game = Game.objects.create(player_x=player_x, player_o=player_o)
        serializer = GameSerializer(game)
        return Response(serializer.data, status=201)

# PUBLIC_INTERFACE
@api_view(['GET'])
def game_detail(request, game_id):
    """GET: Retrieve single game state."""
    game = get_object_or_404(Game, id=game_id)
    serializer = GameSerializer(game)
    return Response(serializer.data)

# PUBLIC_INTERFACE
@api_view(['POST'])
def submit_move(request, game_id):
    """
    POST: Submit a move to a given game (fields: user_id, position).
    Returns updated game, or error if invalid.
    """
    game = get_object_or_404(Game, id=game_id)
    user_id = request.data.get('user_id')
    position = request.data.get('position')
    try:
        user = User.objects.get(id=user_id)
        position = int(position)
    except (User.DoesNotExist, ValueError, TypeError):
        return Response({'error': 'Invalid user or position.'}, status=400)
    try:
        game.make_move(user, position)
    except ValueError as e:
        return Response({'error': str(e)}, status=400)
    serializer = GameSerializer(game)
    return Response(serializer.data)

# PUBLIC_INTERFACE
@api_view(['GET'])
def scoreboard(request):
    """
    GET: Show scoreboard (wins, losses, draws per user).
    """
    users = User.objects.all()
    data = []
    for user in users:
        wins = Game.objects.filter(winner=user).count()
        total_played = Game.objects.filter(Q(player_x=user) | Q(player_o=user), status="FINISHED").count()
        draws = Game.objects.filter(Q(player_x=user) | Q(player_o=user), status="FINISHED", winner__isnull=True).count()
        losses = total_played - wins - draws
        data.append({'username': user.username, 'wins': wins, 'losses': losses, 'draws': draws})
    serializer = ScoreboardSerializer(data, many=True)
    return Response(serializer.data)

# PUBLIC_INTERFACE
@api_view(['GET'])
def game_history(request, user_id=None):
    """GET: Retrieve game history, optionally for a single user."""
    if user_id:
        user = get_object_or_404(User, id=user_id)
        games = Game.objects.filter(Q(player_x=user) | Q(player_o=user)).order_by('-created_at')
    else:
        games = Game.objects.all().order_by('-created_at')
    serializer = GameSerializer(games, many=True)
    return Response(serializer.data)
