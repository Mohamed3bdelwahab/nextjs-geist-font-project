from django.contrib import admin
from .models import Diagram, DiagramVersion, CollaborationSession


@admin.register(Diagram)
class DiagramAdmin(admin.ModelAdmin):
    """Admin interface for Diagram model"""
    
    list_display = ['id', 'title', 'user', 'version', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'updated_at', 'version']
    search_fields = ['title', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'user', 'version', 'is_active')
        }),
        ('Diagram Data', {
            'fields': ('diagram_json',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Customize queryset to show user's own diagrams for non-superusers"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


@admin.register(DiagramVersion)
class DiagramVersionAdmin(admin.ModelAdmin):
    """Admin interface for DiagramVersion model"""
    
    list_display = ['id', 'diagram', 'version_number', 'created_at', 'comment']
    list_filter = ['created_at', 'version_number']
    search_fields = ['diagram__title', 'comment']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Version Information', {
            'fields': ('diagram', 'version_number', 'comment')
        }),
        ('Version Data', {
            'fields': ('diagram_json',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CollaborationSession)
class CollaborationSessionAdmin(admin.ModelAdmin):
    """Admin interface for CollaborationSession model"""
    
    list_display = ['id', 'diagram', 'user', 'session_id', 'joined_at', 'last_activity', 'is_active']
    list_filter = ['is_active', 'joined_at', 'last_activity']
    search_fields = ['diagram__title', 'user__username', 'session_id']
    readonly_fields = ['id', 'joined_at', 'last_activity']
    ordering = ['-last_activity']
    
    fieldsets = (
        ('Session Information', {
            'fields': ('diagram', 'user', 'session_id', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('joined_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Customize queryset for non-superusers"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
