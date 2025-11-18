
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_409_CONFLICT, HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView
from rest_framework.response import Response

from game.api.players.serializers import  PlayerVoteSerializer, GivePlayerHost
from game.models.player import Player, PlayerStatus
from game.models.room import Room
from game.models.votes import Vote

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
        
        if player.status is PlayerStatus.KICKED:
            return Response({"errors": "Kicked players cannot vote"}, HTTP_409_CONFLICT)
        
        voted_player_id = data.get("voted_player_id")

        try:
            voted_player: Player = Player.objects.get(id=voted_player_id)
        except Player.DoesNotExist:
            return Response({"errors": f"Voted Player with id {voted_player_id} does not exist"}, HTTP_404_NOT_FOUND)

        Vote.objects.get_or_create(room=room, player=player, player_voted=voted_player, turn=room.current_round)

        return Response({"message":"Voted Sucessfully"}, HTTP_200_OK)

        
class GivePlayerHostView(APIView):
    def post(self, request, room_code):
        serializer = GivePlayerHost(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            room: list[Room] = Room.objects.get(code=room_code)
        except Room.DoesNotExist:
            return Response({"errors": f"Room with code {room_code} does not exist"}, HTTP_400_BAD_REQUEST)

        room_players = room.players
        
        player_id = data.get("player_id")
        try:
            current_host: Player = room_players.get(id=player_id) 
        except Player.DoesNotExist:
            return Response({"errors": f"Player with id {player_id} does not exist"}, HTTP_404_NOT_FOUND) 

        if not current_host.is_host:
            return Response({"errors": f"Player: {current_host.name} cannot handle host propietary"}, HTTP_401_UNAUTHORIZED)
        
        new_host_id = data.get("host_player_id")
        try:
            new_host:Player = room_players.get(id=new_host_id)
        except Player.DoesNotExist:
            return Response({"errors": f"Player with id {new_host_id} not found"}, HTTP_404_NOT_FOUND)

        current_host.is_host = False
        current_host.save()

        new_host.is_host = False
        new_host.save()

        return Response({"message": "Host property changed successfully"}, HTTP_200_O)
