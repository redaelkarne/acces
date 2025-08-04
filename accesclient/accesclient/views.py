# views.py - Compatibility file for existing URLs
"""
This file maintains backward compatibility with existing URL patterns.
All views have been reorganized into separate modules for better code organization.
"""

# Import all views from the new modular structure
from .views.messages_views import *
from .views.appareil_views import *  
from .views.astreinte_views import *
from .views.auth_views import *
from .views.technician_views import *

# Re-export commonly used classes for backward compatibility
__all__ = [
    # Messages views
    'MessagesView',
    'ArchiveMessagesView', 
    'messages_list',
    'message_detail',
    'create_message',
    'export_messages_to_excel',
    
    # Appareil views
    'AppareilView',
    'modify_appareil',
    'set_appareil_perdu',
    'modify_autres_if_meditrax',
    'export_appareils_to_excel',
    'generate_excel',
    'sanitize_text',
    
    # Astreinte views
    'create_astreinte',
    'upload_excel',
    'view_astreintes',
    'delete_astreinte',
    'modify_astreinte',
    
    # Auth views
    'SignUpView',
    
    # Technician views
    'get_technician_data',
    'ManageTechniciansView',
]
