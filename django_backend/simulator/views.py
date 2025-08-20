from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from .models import Diagram, DiagramVersion, CollaborationSession
import json
import uuid
from datetime import datetime


@api_view(['POST'])
def save_diagram(request):
    """Save or update a diagram"""
    try:
        data = request.data
        diagram_id = data.get('id')
        title = data.get('title', 'Untitled Diagram')
        diagram_json = data.get('diagram_json', '{}')
        
        if diagram_id:
            try:
                diagram = Diagram.objects.get(id=diagram_id)
                DiagramVersion.objects.create(
                    diagram=diagram,
                    version_number=diagram.version,
                    diagram_json=diagram.diagram_json,
                    comment=f"Auto-saved version {diagram.version}"
                )
                diagram.title = title
                diagram.diagram_json = json.dumps(diagram_json) if isinstance(diagram_json, dict) else diagram_json
                diagram.version += 1
                diagram.save()
            except Diagram.DoesNotExist:
                return Response({'error': 'Diagram not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            diagram = Diagram.objects.create(
                user=request.user if request.user.is_authenticated else None,
                title=title,
                diagram_json=json.dumps(diagram_json) if isinstance(diagram_json, dict) else diagram_json,
                version=1
            )
        
        return Response({
            'success': True,
            'diagram': {
                'id': diagram.id,
                'title': diagram.title,
                'version': diagram.version,
                'updated_at': diagram.updated_at
            },
            'message': 'Diagram saved successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': f'Failed to save diagram: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def load_diagram(request, diagram_id=None):
    """Load a specific diagram or list all diagrams"""
    try:
        if diagram_id:
            try:
                diagram = Diagram.objects.get(id=diagram_id, is_active=True)
                return Response({
                    'success': True,
                    'diagram': {
                        'id': diagram.id,
                        'title': diagram.title,
                        'diagram_json': diagram.get_diagram_data(),
                        'version': diagram.version,
                        'created_at': diagram.created_at,
                        'updated_at': diagram.updated_at
                    }
                }, status=status.HTTP_200_OK)
            except Diagram.DoesNotExist:
                return Response({'error': 'Diagram not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            diagrams = Diagram.objects.filter(is_active=True)
            if request.user.is_authenticated:
                diagrams = diagrams.filter(user=request.user)
            
            diagram_list = [{
                'id': d.id,
                'title': d.title,
                'version': d.version,
                'created_at': d.created_at,
                'updated_at': d.updated_at
            } for d in diagrams]
            
            return Response({'success': True, 'diagrams': diagram_list}, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({'error': f'Failed to load diagram: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def diagram_history(request, diagram_id):
    """Get version history for a diagram"""
    try:
        diagram = Diagram.objects.get(id=diagram_id, is_active=True)
        versions = DiagramVersion.objects.filter(diagram=diagram)
        
        version_list = [{
            'version_number': v.version_number,
            'created_at': v.created_at,
            'comment': v.comment
        } for v in versions]
        
        return Response({
            'success': True,
            'diagram_id': diagram_id,
            'current_version': diagram.version,
            'versions': version_list
        }, status=status.HTTP_200_OK)
        
    except Diagram.DoesNotExist:
        return Response({'error': 'Diagram not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Failed to get diagram history: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_new_diagram(request):
    """Create a new blank diagram"""
    try:
        title = request.data.get('title', 'New Diagram')
        diagram_type = request.data.get('type', 'flowchart')
        
        initial_data = {
            'shapes': [],
            'connections': [],
            'canvas': {'width': 1200, 'height': 800, 'background': '#ffffff', 'grid': True},
            'type': diagram_type,
            'metadata': {'created': datetime.now().isoformat(), 'version': 1}
        }
        
        diagram = Diagram.objects.create(
            user=request.user if request.user.is_authenticated else None,
            title=title,
            diagram_json=json.dumps(initial_data),
            version=1
        )
        
        return Response({
            'success': True,
            'diagram': {
                'id': diagram.id,
                'title': diagram.title,
                'version': diagram.version,
                'created_at': diagram.created_at
            },
            'message': 'New diagram created successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': f'Failed to create diagram: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_diagram(request, diagram_id):
    """Delete a diagram (soft delete)"""
    try:
        diagram = Diagram.objects.get(id=diagram_id, is_active=True)
        diagram.is_active = False
        diagram.save()
        
        return Response({
            'success': True,
            'message': 'Diagram deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Diagram.DoesNotExist:
        return Response({'error': 'Diagram not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Failed to delete diagram: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def export_diagram(request, diagram_id, format_type):
    """Export diagram in various formats"""
    try:
        diagram = Diagram.objects.get(id=diagram_id, is_active=True)
        
        if format_type.lower() == 'json':
            return Response({
                'success': True,
                'data': diagram.get_diagram_data(),
                'format': 'json',
                'filename': f"{diagram.title.replace(' ', '_')}_v{diagram.version}.json"
            }, status=status.HTTP_200_OK)
            
        elif format_type.lower() == 'xml':
            xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<diagram title="{diagram.title}" version="{diagram.version}">
    <data>{diagram.diagram_json}</data>
</diagram>"""
            
            return Response({
                'success': True,
                'data': xml_data,
                'format': 'xml',
                'filename': f"{diagram.title.replace(' ', '_')}_v{diagram.version}.xml"
            }, status=status.HTTP_200_OK)
            
        else:
            return Response({'error': f'Unsupported export format: {format_type}'}, status=status.HTTP_400_BAD_REQUEST)
            
    except Diagram.DoesNotExist:
        return Response({'error': 'Diagram not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Failed to export diagram: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'service': 'Diagram Simulator API',
        'timestamp': datetime.now().isoformat()
    }, status=status.HTTP_200_OK)
