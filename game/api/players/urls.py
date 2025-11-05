
from django.urls import path

from game.api.players.views import CreatePlayerRoomView, VotePlayerView


urlpatterns = [
    path("<room_code>/", CreatePlayerRoomView.as_view(), name='create_room_player'),
    path("<room_code>/vote/", VotePlayerView.as_view(), name='player_vote')
]