from rest_framework import serializers


class PlayerSerializer(serializers.Serializer):
    name = serializers.CharField()

class PlayerVoteSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    voted_player_id = serializers.IntegerField()