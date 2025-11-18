

from django.db import models
from .room import Room

class PlayerStatus(models.Choices):
    ACTIVE = "ACTIVE"
    KICKED = "KICKED"

class RolesChoices(models.TextChoices):
    PARTICIPANT = 'PART'
    IMPOSTOR = 'IMP'

class Player(models.Model):
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE, null=True, blank=True, related_name='players')

    name = models.CharField(max_length=255) 
    is_host = models.BooleanField(default=False)
    role = models.CharField(choices=RolesChoices.choices, default=None, null=True, blank=True)
    status = models.CharField(choices=PlayerStatus.choices, default=PlayerStatus.ACTIVE)

    class Meta:
        db_table = 'players'

        constraints = [
            models.UniqueConstraint(
                fields=["name", "room"],
                name="unique_player_name_per_room"
            )
        ]

    
    def __str__(self):
        return f"({self.name}) ({self.is_host})"