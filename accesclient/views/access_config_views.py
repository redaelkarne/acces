# access_config_views.py
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
import json
import os
from django.conf import settings


@staff_member_required
def manage_access_config(request):
    """Manage access_config.json file"""
    json_path = os.path.join(settings.BASE_DIR, 'access_config.json')
    
    # Load current config
    config = {}
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            messages.error(request, f"Erreur lors de la lecture du fichier: {e}")
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_user':
            # Add a new user to config
            new_user = request.POST.get('new_user', '').strip()
            if new_user and new_user not in config:
                config[new_user] = []
                messages.success(request, f"Utilisateur '{new_user}' ajouté avec succès")
        
        elif action == 'delete_user':
            # Delete a user from config
            user_to_delete = request.POST.get('user_to_delete')
            if user_to_delete in config:
                del config[user_to_delete]
                messages.success(request, f"Utilisateur '{user_to_delete}' supprimé avec succès")
        
        elif action == 'add_access':
            # Add access to a user
            username = request.POST.get('username')
            new_access = request.POST.get('new_access', '').strip()
            if username in config and new_access:
                if new_access not in config[username]:
                    config[username].append(new_access)
                    messages.success(request, f"Accès '{new_access}' ajouté pour '{username}'")
                else:
                    messages.warning(request, f"Accès '{new_access}' existe déjà pour '{username}'")
        
        elif action == 'remove_access':
            # Remove access from a user
            username = request.POST.get('username')
            access_to_remove = request.POST.get('access_to_remove')
            if username in config and access_to_remove in config[username]:
                config[username].remove(access_to_remove)
                messages.success(request, f"Accès '{access_to_remove}' retiré de '{username}'")
        
        # Save config back to file
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messages.error(request, f"Erreur lors de la sauvegarde: {e}")
        
        return redirect('manage_access_config')
    
    # Sort config by username for display
    sorted_config = dict(sorted(config.items()))
    
    context = {
        'config': sorted_config,
    }
    
    return render(request, 'accesclient/manage_access_config.html', context)
