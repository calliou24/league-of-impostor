

from rest_framework import serializers

from game.models.room import Room


class StartGameSerializer(serializers.Serializer): 
    player_id = serializers.IntegerField()

class CreateRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model=Room
        fields=['code']