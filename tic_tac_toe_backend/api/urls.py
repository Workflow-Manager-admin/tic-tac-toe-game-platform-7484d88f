from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health, name='Health'),
    path('users/', views.users_list_create, name='User-List-Create'),
    path('games/', views.games_list_create, name='Game-List-Create'),
    path('games/<int:game_id>/', views.game_detail, name='Game-Detail'),
    path('games/<int:game_id>/move/', views.submit_move, name='Game-Move'),
    path('scoreboard/', views.scoreboard, name='Scoreboard'),
    path('games/history/', views.game_history, name='Game-History-Global'),
    path('games/history/<int:user_id>/', views.game_history, name='Game-History-User'),
]
