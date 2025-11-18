


from django.urls.conf import path

from game.api.rooms.views import CreateRoomView, JoinRoomView, StartRoomGameView, StartVoteStage, FinishVoting


urlpatterns = [ 
    path("", CreateRoomView.as_view(), name='create_room'),
    path("<room_code>/join/", JoinRoomView.as_view(), name='join_player'),
    path("<room_code>/start/", StartRoomGameView.as_view(), name='start_room_game'),
    path("<room_code>/vote/", StartVoteStage.as_view(), name='start_vote_stage'),
    path("<room_code>/finish-voting/", FinishVoting.as_view(), name='finish_voting_stage')
]