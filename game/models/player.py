

from django.db import models
from .room import Room


class Player(models.Model):
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE, null=True, blank=True, related_name='players')

    name = models.CharField() 
    is_host = models.BooleanField(default=False)

    class Meta:
        db_table = 'players'

    
    def __str__(self):
        return f"({self.name}) ({self.is_host})"