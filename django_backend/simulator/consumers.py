import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Diagram, CollaborationSession
from datetime import datetime


class DiagramConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time diagram collaboration"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.diagram_id = self.scope['url_route']['kwargs']['diagram_id']
        self.room_group_name = f'diagram_{self.diagram_id}'
        self.session_id = str(uuid.uuid4())
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept WebSocket connection
        await self.accept()
        
        # Create collaboration session
        await self.create_collaboration_session()
        
        # Notify other users about new participant
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'session_id': self.session_id,
                'message': 'A user joined the collaboration'
            }
        )
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Update collaboration session
        await self.end_collaboration_session()
        
        # Notify other users about participant leaving
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'session_id': self.session_id,
                'message': 'A user left the collaboration'
            }
        )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'diagram_update')
            
            if message_type == 'diagram_update':
                await self.handle_diagram_update(text_data_json)
            elif message_type == 'cursor_position':
                await self.handle_cursor_update(text_data_json)
            elif message_type == 'selection_change':
                await self.handle_selection_change(text_data_json)
            elif message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            else:
                await self.send_error('Unknown message type')
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            await self.send_error(f'Error processing message: {str(e)}')
    
    async def handle_diagram_update(self, data):
        """Handle diagram update messages"""
        try:
            diagram_data = data.get('diagram_data', {})
            operation = data.get('operation', 'update')
            shape_id = data.get('shape_id')
            
            # Update diagram in database if needed
            if operation in ['save', 'auto_save']:
                await self.save_diagram_update(diagram_data)
            
            # Broadcast update to all users in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'diagram_update_broadcast',
                    'diagram_data': diagram_data,
                    'operation': operation,
                    'shape_id': shape_id,
                    'session_id': self.session_id,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            await self.send_error(f'Error handling diagram update: {str(e)}')
    
    async def handle_cursor_update(self, data):
        """Handle cursor position updates"""
        cursor_data = {
            'x': data.get('x', 0),
            'y': data.get('y', 0),
            'session_id': self.session_id
        }
        
        # Broadcast cursor position to other users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'cursor_update_broadcast',
                'cursor_data': cursor_data
            }
        )
    
    async def handle_selection_change(self, data):
        """Handle shape selection changes"""
        selection_data = {
            'selected_shapes': data.get('selected_shapes', []),
            'session_id': self.session_id
        }
        
        # Broadcast selection to other users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'selection_change_broadcast',
                'selection_data': selection_data
            }
        )
    
    async def handle_chat_message(self, data):
        """Handle chat messages"""
        message = data.get('message', '')
        username = data.get('username', 'Anonymous')
        
        # Broadcast chat message to all users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message_broadcast',
                'message': message,
                'username': username,
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    # Broadcast handlers
    async def diagram_update_broadcast(self, event):
        """Send diagram update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'diagram_update',
            'diagram_data': event['diagram_data'],
            'operation': event['operation'],
            'shape_id': event.get('shape_id'),
            'session_id': event['session_id'],
            'timestamp': event['timestamp']
        }))
    
    async def cursor_update_broadcast(self, event):
        """Send cursor update to WebSocket"""
        # Don't send cursor updates back to the sender
        if event['cursor_data']['session_id'] != self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'cursor_update',
                'cursor_data': event['cursor_data']
            }))
    
    async def selection_change_broadcast(self, event):
        """Send selection change to WebSocket"""
        # Don't send selection updates back to the sender
        if event['selection_data']['session_id'] != self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'selection_change',
                'selection_data': event['selection_data']
            }))
    
    async def chat_message_broadcast(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'session_id': event['session_id'],
            'timestamp': event['timestamp']
        }))
    
    async def user_joined(self, event):
        """Send user joined notification"""
        if event['session_id'] != self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'message': event['message'],
                'session_id': event['session_id']
            }))
    
    async def user_left(self, event):
        """Send user left notification"""
        if event['session_id'] != self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'message': event['message'],
                'session_id': event['session_id']
            }))
    
    async def send_error(self, error_message):
        """Send error message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        }))
    
    @database_sync_to_async
    def create_collaboration_session(self):
        """Create collaboration session in database"""
        try:
            diagram = Diagram.objects.get(id=self.diagram_id)
            user = self.scope.get('user') if self.scope.get('user') and self.scope['user'].is_authenticated else None
            
            CollaborationSession.objects.create(
                diagram=diagram,
                user=user,
                session_id=self.session_id,
                is_active=True
            )
        except Diagram.DoesNotExist:
            pass
        except Exception:
            pass
    
    @database_sync_to_async
    def end_collaboration_session(self):
        """End collaboration session in database"""
        try:
            session = CollaborationSession.objects.get(session_id=self.session_id)
            session.is_active = False
            session.save()
        except CollaborationSession.DoesNotExist:
            pass
        except Exception:
            pass
    
    @database_sync_to_async
    def save_diagram_update(self, diagram_data):
        """Save diagram update to database"""
        try:
            diagram = Diagram.objects.get(id=self.diagram_id)
            diagram.diagram_json = json.dumps(diagram_data)
            diagram.save()
        except Diagram.DoesNotExist:
            pass
        except Exception:
            pass
