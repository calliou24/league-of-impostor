from rest_framework.generics import CreateAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import APIView 

from game.api.rooms.serializers import CreateRoomSerializer, StartGameSerializer
from game.models.player import Player
from game.models.room import Room, RoomStageCoices
from game.models.votes import Vote
from league_impostor.services.characters import get_random_league_champion


class CreateRoomView(CreateAPIView):
    queryset=Room.objects.all()
    serializer_class=CreateRoomSerializer

    def perform_create(self, serializer):
        try:
            Room.objects.get(code=self.request.data.get("code"))
            raise ValidationError("Room code its not available")
        except Room.DoesNotExist:
            ""

        serializer.save()

class StartRoomGameView(APIView):
    def post(self, request, room_code):
        serializer = StartGameSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, HTTP_400_BAD_REQUEST)

        request_data = serializer.validated_data
        try:
            room = Room.objects.get(code=room_code)
        except Room.DoesNotExist:
            return Response({"error": f"Room with id {room_code} does not exist"}, HTTP_404_NOT_FOUND)

        player_id = request_data.get("player_id")

        try: 
            player: Player = Player.objects.get(id=player_id, room=room)
        except Player.DoesNotExist:
            return Response({"error": f"Player with id {player_id} does not exist in this room"}, HTTP_404_NOT_FOUND)

        if not player.is_host:
            return Response({"error": "Only host player can start the game"}, HTTP_500_INTERNAL_SERVER_ERROR)

        try:
           character = get_random_league_champion()
        except Exception as e:
            return Response({"error": e}, HTTP_500_INTERNAL_SERVER_ERROR)

        if room.stage == RoomStageCoices.ROUND:
            return Response({"error": "Room round already started"}, HTTP_409_CONFLICT)
        
        room.character = character
        room.stage = RoomStageCoices.ROUND
        room.save()

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
    def post(self, _, room_code):

        try:
            room = Room.objects.get(code=room_code)
        except Room.DoesNotExist:
            return Response({"errors": f"Room with code {room_code} does not exist"}, HTTP_400_BAD_REQUEST)

        if room.stage != RoomStageCoices.VOTING:
            return Response({"errors": f"Room in stage {room.sage} cannot finish voting"}, HTTP_500_INTERNAL_SERVER_ERROR)

        votes: list[Vote] = Vote.objects.filter(turn=room.current_round, room=room)

        if len(votes) <= 0:
            return Response({"errors": "Players havent vote"}, HTTP_500_INTERNAL_SERVER_ERROR)
        players = {}
        for _, vote in votes:
            players[vote.voted_player] += 1

        print(players)
