import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CommandSuggestion, Session

class SessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'session_{self.room_code}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'chat_message':
            message = text_data_json.get('message')
            sender = self.scope['user'].username
            
            # Save message to DB (optional)
            # Check for command suggestions if enabled by host
            suggestion = await self.get_command_suggestion(message, self.room_code)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender,
                    'suggestion': suggestion
                }
            )
        
        elif message_type == 'signal':
            # Signaling for WebRTC (offer, answer, candidate)
            # We target a specific user if 'target' is present, otherwise broadcast (careful with broadcast)
            target = text_data_json.get('target')
            sender = self.scope['user'].username
            
            payload = {
                'type': 'signal',
                'sender': sender,
                'data': text_data_json.get('data'),
                'target': target
            }
            
            if target:
                # Send to specific channel if we tracked it (need to store channel_names in DB or Redis)
                # For simplicity in this demo without Redis channel layer specific addressing:
                # We broadcast and let clients filter by 'target'
                await self.channel_layer.group_send(
                    self.room_group_name,
                    payload
                )
            else:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    payload
                )

        elif message_type == 'user_join':
             await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_join',
                    'username': self.scope['user'].username,
                    'channel_name': self.channel_name # Useful if we want to target
                }
            )
            
        elif message_type == 'audio_message':
             await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'audio_message',
                    'content': text_data_json.get('content'),
                    'sender': self.scope['user'].username
                }
            )

        elif message_type == 'participant_update':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'participant_update',
                    'username': text_data_json.get('username'),
                    'action': text_data_json.get('action'),
                    'sender': self.scope['user'].username
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'suggestion': event.get('suggestion')
        }))

    async def audio_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'audio_message',
            'content': event['content'],
            'sender': event['sender']
        }))

    async def signal(self, event):
        # Only send if I am the target or if it's broadcast (and I'm not the sender)
        if event.get('target') and event['target'] != self.scope['user'].username:
            return
        if event['sender'] == self.scope['user'].username:
            return
            
        await self.send(text_data=json.dumps({
            'type': 'signal',
            'sender': event['sender'],
            'data': event['data']
        }))

    async def user_join(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'username': event['username'],
            'channel_name': event.get('channel_name')
        }))

    async def participant_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'participant_update',
            'username': event['username'],
            'action': event['action'],
            'sender': event['sender']
        }))



    @database_sync_to_async
    def get_command_suggestion(self, text, room_code):
        try:
            session = Session.objects.get(room_code=room_code)
            if not session.is_suggestions_enabled:
                return None
        except Session.DoesNotExist:
            return None

        # Simple keyword matching with word boundary check
        import re
        suggestions = CommandSuggestion.objects.all()
        text = text.lower()
        
        for s in suggestions:
            # Match keyword as a whole word (case insensitive)
            pattern = r'\b' + re.escape(s.keyword.lower()) + r'\b'
            if re.search(pattern, text):
                return f"Tip: {s.suggestion} - {s.description}"
        
        # Hardcoded fallback for common terms if DB is missing some
        if re.search(r'\btaskbar\b', text):
            return "Tip: Win+T to focus taskbar."
            
        return None
