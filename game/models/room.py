from django.db import models

class RoomStageCoices(models.TextChoices):
    LOBBY = 'LOBBY'
    VOTING = 'VOTING'
    ROUND = 'ROUND'

class Room(models.Model):
    code = models.CharField(unique=True, default="Text")
    stage = models.CharField(choices=RoomStageCoices, default=RoomStageCoices.LOBBY)
    character = models.CharField(null=True, blank=True)
    current_round = models.IntegerField(default=1)

    class Meta:
        db_table='rooms'

        indexes = [
            models.Index(
                fields=['code'],
                name='room_code'
            )
        ]

        constraints = [
            models.UniqueConstraint(
                fields=['code'],
                name="unique_room_code"
            )
        ]

    def __str__(self):
        return f"({self.code})"