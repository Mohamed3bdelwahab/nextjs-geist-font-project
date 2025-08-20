from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class Diagram(models.Model):
    """
    Model to store diagram data with version control
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, default="Untitled Diagram")
    diagram_json = models.TextField(help_text="JSON representation of the diagram")
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
        
    def __str__(self):
        return f"{self.title} (v{self.version})"
    
    def get_diagram_data(self):
        """Parse and return diagram JSON data"""
        try:
            return json.loads(self.diagram_json)
        except json.JSONDecodeError:
            return {}
    
    def set_diagram_data(self, data):
        """Set diagram data from dictionary"""
        self.diagram_json = json.dumps(data)


class DiagramVersion(models.Model):
    """
    Model to track version history of diagrams
    """
    diagram = models.ForeignKey(Diagram, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    diagram_json = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-version_number']
        unique_together = ['diagram', 'version_number']
        
    def __str__(self):
        return f"{self.diagram.title} - Version {self.version_number}"


class CollaborationSession(models.Model):
    """
    Model to track active collaboration sessions
    """
    diagram = models.ForeignKey(Diagram, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=255, unique=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-last_activity']
        
    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{username} - {self.diagram.title}"
