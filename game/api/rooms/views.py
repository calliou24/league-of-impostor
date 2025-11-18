
from random import randint 
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView 
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import game.api.rooms.serializers as room_serializers
from game.models.player import Player, RolesChoices, PlayerStatus
from game.models.room import Room, RoomStageCoices
from game.models.votes import Vote
from league_impostor.services.characters import get_random_league_champion


class CreateRoomView(APIView):
    def post(self, request):
        serializer = room_serializers.CreateRoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        room_code = data.get("code")
        try:
            Room.objects.get(code=room_code)
            return Response({"errors": f"Room with code {room_code} already exist"}, HTTP_409_CONFLICT)
        except Room.DoesNotExist:
            pass

        room = Room.objects.create(code=room_code)

        player_name = data.get("player_name")
        host_player = Player.objects.create(name=player_name, room=room, is_host=True)

        return Response({"player_id": host_player.pk, "player_name": player_name, "room_code": room_code}, HTTP_201_CREATED)

class JoinRoomView(APIView):
    def post(self, request, room_code):
        serializer = room_serializers.JoinRoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        try: 
            room = Room.objects.get(code=room_code)
        except Room.DoesNotExist:
            return Response({"errors": f"Room with code {room_code} does not exist"}, HTTP_404_NOT_FOUND)
        
        player_name = data.get("player_name")
        try:
            Player.objects.get(name=player_name)
            return Response({"errors": f"A player with the name {player_name} already joined the room"}, HTTP_409_CONFLICT)
        except Player.DoesNotExist:
            pass

        player = Player.objects.create(name=player_name, room=room)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"room_{room_code}", 
            {
                "type": "room_event",
                'data': {
                    'event': 'player_added',
                    "player_id": player.id,
                    "player_name": player.name,
                  }
            }
        )


        return Response({"player_id": player.pk, "player_name": player.name , "room_code": room_code}, HTTP_200_OK)
        

class StartRoomGameView(APIView):
    def post(self, request, room_code):
        serializer = room_serializers.StartGameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request_data = serializer.validated_data
        try:
            room = Room.objects.get(code=room_code)
        except Room.DoesNotExist:
            return Response({"errors": f"Room with id {room_code} does not exist"}, HTTP_404_NOT_FOUND)

        player_id = request_data.get("player_id")

        try: 
            player: Player = Player.objects.get(id=player_id, room=room)
        except Player.DoesNotExist:
            return Response({"errors": f"Player with id {player_id} does not exist in this room"}, HTTP_404_NOT_FOUND)

        if not player.is_host:
            return Response({"errors": "Only host player can start the game"}, HTTP_500_INTERNAL_SERVER_ERROR)

        room_players: list[Player] = Player.objects.filter(room=room)
        players_count = room_players.count()

        if players_count < 3:
            return Response({"errors": "To start the room 3 players must be in the room"}, HTTP_500_INTERNAL_SERVER_ERROR)

        try:
           character = get_random_league_champion()
        except Exception as e:
            return Response({"errors": e}, HTTP_500_INTERNAL_SERVER_ERROR)

        if room.stage == RoomStageCoices.ROUND:
            return Response({"errors": "Room round already started"}, HTTP_409_CONFLICT)
        
        room.character = character
        room.stage = RoomStageCoices.ROUND
        room.save()


        impostor_inx = randint(0, players_count - 1)
        impostor = room_players[impostor_inx]
        
        for player in room_players:
            if impostor.pk == player.pk:
                player.role = RolesChoices.IMPOSTOR
                player.save()
            else: 
                player.role = RolesChoices.PARTICIPANT
                player.save()

        return Response({"success": True, "character": character}, HTTP_200_OK)

class StartVoteStage(APIView):
    def post(self, _, room_code):
        try:
            room = Room.objects.get(code=room_code)
        except Room.DoesNotExist: 
            return Response({"errors": f"Room with code {room_code} does not exist"}, HTTP_400_BAD_REQUEST)

        if room.stage != RoomStageCoices.ROUND:
            return Response({"errors": f"Its not possible to start voting stage from this sage {room.stage}"}, HTTP_500_INTERNAL_SERVER_ERROR)
        
        room.stage = RoomStageCoices.VOTING
        room.save()

        return Response({"success": True, "message": "Vote Stage started"}, HTTP_200_OK)
        
class FinishVoting(APIView):
    def post(self, request, room_code):
        serializer = room_serializers.EndVotingStageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        player_id = data.get("player_id")
        try:
            host_player = Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return Response({"errors": "Player with id {player_id} does not exist"}, HTTP_404_NOT_FOUND)

        if not host_player.is_host:
            return Response({"errors": "Only the host can end the voting stage"}, HTTP_401_UNAUTHORIZED)

        try:
            room = Room.objects.get(code=room_code)
        except Room.DoesNotExist:
            return Response({"errors": f"Room with code {room_code} does not exist"}, HTTP_400_BAD_REQUEST)

        if room.stage != RoomStageCoices.VOTING:
            return Response({"errors": f"Room in stage {room.sage} cannot finish voting"}, HTTP_500_INTERNAL_SERVER_ERROR)

        votes: list[Vote] = Vote.objects.filter(turn=room.current_round, room=room)

        players_count = room.players.all().count()

        if len(votes) <= 0 or players_count < len(votes):
            return Response({"errors": "All players have to vote"}, HTTP_500_INTERNAL_SERVER_ERROR)

        room_players: list[Player] = room.players.all()

        highest_voted = {
            "pk": 0,
            "votes": 0
        }
        for player in room_players:
            player_voted_count = votes.filter(player_voted=player).count()
            if highest_voted["votes"] <= player_voted_count:
                highest_voted["pk"] = player.pk
                highest_voted["votes"] = player_voted_count

        try:        
            voted_player:Player = room_players.get(id=highest_voted["pk"])
        except Player.DoesNotExist:
            return Response({"errors": "Error obtaining most voted player"}, HTTP_500_INTERNAL_SERVER_ERROR)

        impostor_player:Player = room_players.get(role=RolesChoices.IMPOSTOR)

        if impostor_player.pk == voted_player.pk:
            room_players.update(role=RolesChoices.PARTICIPANT)
            room.stage = RoomStageCoices.LOBBY
            room.save()
            return Response({"message": "Impostor founded, congrats"}, HTTP_200_OK)

        voted_player.status = PlayerStatus.KICKED
        voted_player.save()

        room.stage = RoomStageCoices.ROUND
        room.save()

        return Response({"errors": "Voted player was not the impostor"}, HTTP_200_OK)
