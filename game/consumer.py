import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class RoomConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f"room_{self.room_code}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def room_event(self,event):
        print("room event", event)
        await self.send(text_data=json.dumps(event["data"]))