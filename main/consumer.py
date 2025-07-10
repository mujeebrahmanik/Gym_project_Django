# main/consumer.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync

class TrainerNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name='notification'
        await self.channel_layer.group_add(
            self.group_name, self.channel_name
        )
        await self.accept()
        


        print("✅ WebSocket connected")

    async def receive(self, text_data=None, bytes_data=None):
        print("✅ WebSocket recieved")
       

    async def disconnect(self, close_code):
        print("❌ WebSocket disconnected")
        
        
    async def send_notification(self,event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'id':event['id'],
            'date':event['date'],
            'total':event['total']
        }))

