from rest_framework import serializers
from .models import Diagram, DiagramVersion, CollaborationSession
from django.contrib.auth.models import User


class DiagramSerializer(serializers.ModelSerializer):
    """Serializer for Diagram model"""
    
    diagram_data = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Diagram
        fields = [
            'id', 'title', 'diagram_json', 'diagram_data', 'version', 
            'created_at', 'updated_at', 'user', 'user_name', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'version']
    
    def get_diagram_data(self, obj):
        """Return parsed diagram JSON data"""
        return obj.get_diagram_data()
    
    def get_user_name(self, obj):
        """Return username if user exists"""
        return obj.user.username if obj.user else 'Anonymous'


class DiagramVersionSerializer(serializers.ModelSerializer):
    """Serializer for DiagramVersion model"""
    
    diagram_title = serializers.SerializerMethodField()
    
    class Meta:
        model = DiagramVersion
        fields = [
            'id', 'diagram', 'diagram_title', 'version_number', 
            'diagram_json', 'created_at', 'comment'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_diagram_title(self, obj):
        """Return diagram title"""
        return obj.diagram.title


class CollaborationSessionSerializer(serializers.ModelSerializer):
    """Serializer for CollaborationSession model"""
    
    user_name = serializers.SerializerMethodField()
    diagram_title = serializers.SerializerMethodField()
    
    class Meta:
        model = CollaborationSession
        fields = [
            'id', 'diagram', 'diagram_title', 'user', 'user_name', 
            'session_id', 'joined_at', 'last_activity', 'is_active'
        ]
        read_only_fields = ['id', 'joined_at', 'last_activity']
    
    def get_user_name(self, obj):
        """Return username if user exists"""
        return obj.user.username if obj.user else 'Anonymous'
    
    def get_diagram_title(self, obj):
        """Return diagram title"""
        return obj.diagram.title


class DiagramCreateSerializer(serializers.Serializer):
    """Serializer for creating new diagrams"""
    
    title = serializers.CharField(max_length=255, required=False, default='New Diagram')
    type = serializers.CharField(max_length=50, required=False, default='flowchart')
    diagram_json = serializers.JSONField(required=False, default=dict)
    
    def validate_type(self, value):
        """Validate diagram type"""
        valid_types = [
            'flowchart', 'uml', 'network', 'orgchart', 'mindmap', 
            'wireframe', 'gantt', 'er', 'bpmn', 'basic'
        ]
        if value.lower() not in valid_types:
            raise serializers.ValidationError(f"Invalid diagram type. Must be one of: {', '.join(valid_types)}")
        return value.lower()


class DiagramUpdateSerializer(serializers.Serializer):
    """Serializer for updating diagrams"""
    
    id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=255, required=False)
    diagram_json = serializers.JSONField(required=True)
    comment = serializers.CharField(max_length=500, required=False, default='')
    
    def validate_diagram_json(self, value):
        """Validate diagram JSON structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("diagram_json must be a valid JSON object")
        
        # Basic structure validation
        required_keys = ['shapes', 'connections', 'canvas']
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f"diagram_json must contain '{key}' field")
        
        return value
