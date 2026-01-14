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
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect

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
    'create_appareil',
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

def login_view(request):
    print("--- DEBUG: login_view (views.py) APPELÉE ---")
    
    # Sécurité : Si l'utilisateur est déjà connecté mais n'a pas d'email valide
    if request.user.is_authenticated:
        print(f"DEBUG: Utilisateur déjà connecté: {request.user.username}, Email: '{request.user.email}'")
        if not request.user.email or '@' not in request.user.email:
            print("DEBUG: Email invalide pour l'utilisateur connecté. Déconnexion forcée.")
            logout(request)
        else:
            print("DEBUG: Email valide. Redirection.")
            return redirect('messages_ascenseurs')

    if request.method == 'POST':
        print("DEBUG: Requête POST reçue")
        print(f"DEBUG: Données POST: {list(request.POST.keys())}")

        # Cas 1: Mise à jour de l'email depuis le modal
        if 'update_email' in request.POST:
            print("DEBUG: Traitement de la mise à jour d'email")
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            
            # Validation basique de l'email reçu
            if not email or '@' not in email:
                messages.error(request, "Email invalide.")
                return render(request, 'login.html', {
                    'show_email_modal': True,
                    'username': username,
                    'password': password
                })

            users = User.objects.filter(last_name=username)
            target_user = None
            for u in users:
                if u.check_password(password):
                    target_user = u
                    break
            
            if target_user:
                target_user.email = email
                target_user.save()
                if request.user.is_authenticated:
                    logout(request)
                auth_login(request, target_user, backend='accesclient.backends.LastNameAuthBackend')
                messages.success(request, "Email mis à jour avec succès !")
                return redirect('messages_ascenseurs')
            else:
                messages.error(request, "Erreur lors de la mise à jour.")
                return render(request, 'login.html')
        
        # Cas 2: Tentative de connexion normale
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
            print(f"DEBUG: Tentative de connexion pour: '{username}'")
            
            users = User.objects.filter(last_name=username)
            print(f"DEBUG: Nombre d'utilisateurs trouvés avec ce nom: {users.count()}")
            
            user_found = None
            for u in users:
                if u.check_password(password):
                    user_found = u
                    print(f"DEBUG: Mot de passe correct pour ID: {u.pk}")
                    break
            
            if user_found:
                # VERIFICATION STRICTE DE L'EMAIL
                email_actuel = user_found.email
                print(f"DEBUG: Email brut en base: '{email_actuel}' (Type: {type(email_actuel)})")
                
                if email_actuel:
                    email_actuel = email_actuel.strip()
                
                print(f"DEBUG: Email après nettoyage: '{email_actuel}'")

                # Si vide, None ou pas de @ -> BLOQUER IMPERATIVEMENT
                if not email_actuel or '@' not in email_actuel:
                    print("DEBUG: >>> EMAIL INVALIDE OU MANQUANT. BLOCAGE DE LA CONNEXION. <<<")
                    print("DEBUG: Affichage du modal.")
                    return render(request, 'login.html', {
                        'show_email_modal': True,
                        'username': username,
                        'password': password
                    })
                
                print("DEBUG: Email valide. Connexion autorisée.")
                if request.user.is_authenticated:
                    logout(request)
                    
                auth_login(request, user_found, backend='accesclient.backends.LastNameAuthBackend')
                return redirect('messages_ascenseurs')
            else:
                print("DEBUG: Utilisateur non trouvé ou mot de passe incorrect")
                messages.error(request, "Nom ou mot de passe incorrect.")
    
    return render(request, 'login.html')
