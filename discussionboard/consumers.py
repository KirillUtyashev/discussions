from channels.generic.websocket import AsyncWebsocketConsumer
import json


class DiscussionBoardConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        course_slug = self.scope['url_route']['kwargs']['course_slug']
        self.room_group_name = f'discussionboard-{course_slug}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print(f'disconnected with code {close_code}')

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'discussionboard_message',
            'message': message
        })

    async def discussionboard_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({'message': message}))

    async def create_thread(self):
        pass

    async def save_thread(self):
        pass
