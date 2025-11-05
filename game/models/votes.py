

from django.db import models
from .room import Room
from .player import Player


class Vote(models.Model):
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE, related_name="votes")
    
    player = models.ForeignKey(to=Player, on_delete=models.CASCADE, related_name='player')
    player_voted = models.ForeignKey(to=Player, on_delete=models.CASCADE, related_name='player_voted') 
    turn = models.IntegerField()

    class Meta:
        db_table = 'votes'

    def __str__(self):
        return f"({self.player}) ({self.player_voted}) ({self.turn})"