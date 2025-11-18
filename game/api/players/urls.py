
from django.urls import path

from game.api.players.views import VotePlayerView


urlpatterns = [
    path("<room_code>/vote/", VotePlayerView.as_view(), name='player_vote')
]