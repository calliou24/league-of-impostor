
import json
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.response import Response

from game.api.players.serializers import PlayerSerializer, PlayerVoteSerializer
from game.models.player import Player
from game.models.room import Room
from game.models.votes import Vote

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class CreatePlayerRoomView(APIView):
    def post(self, request, room_code):
        serializer = PlayerSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.error, HTTP_400_BAD_REQUEST)

        try:
            room = Room.objects.get(code=room_code)
        except Room.DoesNotExist:
            return Response({"errors":f"Room with code: {room_code} does not exist"}, HTTP_400_BAD_REQUEST)

        room_players = room.players.all()
        

        name = serializer.validated_data.get("name")
        is_host = True if len(room_players) == 0 else False

        player = Player.objects.create(name=name, is_host=is_host)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"room_{room_code}", 
            {
                "type": "room_event",
                'data': {
                    'event': 'player added',
                    "player_id": player.id,
                    "player_name": player.name,
                  }
            }
        )
        return Response({"sucess": True, "message": "Player created"}, HTTP_201_CREATED)

class VotePlayerView(APIView):
    def post(self, request, room_code): 
        serializer = PlayerVoteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, HTTP_400_BAD_REQUEST)

        try: 
            room: Room = Room.objects.get(code=room_code)
        except Room.DoesNotExist:
            return Response({"errors": f"Room with code {room_code} does not exist"}, HTTP_400_BAD_REQUEST)

        data = serializer.validated_data 
        player_id = data.get("player_id")

        try:
            player: Player = Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return Response({"errors": f"Player with id {player_id} does not exist"}, HTTP_404_NOT_FOUND)
        
        voted_player_id = data.get("voted_player_id")

        try:
            voted_player: Player = Player.objects.get(id=voted_player_id)
        except Player.DoesNotExist:
            return Response({"errors": f"Voted Player with id {voted_player_id} does not exist"}, HTTP_404_NOT_FOUND)

        vote = Vote.objects.create(room=room, player=player, player_vote=voted_player, turn=room.current_round)

        