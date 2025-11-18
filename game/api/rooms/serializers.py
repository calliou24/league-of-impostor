

from rest_framework import serializers

class StartGameSerializer(serializers.Serializer): 
    player_id = serializers.IntegerField()

class CreateRoomSerializer(serializers.Serializer):
    code = serializers.CharField()
    player_name = serializers.CharField()

class JoinRoomSerializer(serializers.Serializer):
    player_name = serializers.CharField()
    
class EndVotingStageSerializer(serializers.Serializer):
    player_id = serializers.CharField()