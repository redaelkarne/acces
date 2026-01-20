# auth_views.py
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.messages import get_messages

from ..forms import CustomUserCreationForm


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


def logout_view(request):
    """Vue personnalisée pour vider les messages avant déconnexion"""
    # Vider tous les messages de la session
    storage = get_messages(request)
    for _ in storage:
        pass  # Itérer pour marquer les messages comme utilisés
    storage.used = True
    
    logout(request)
    return redirect('login')


def login_view(request):
    print("--- DEBUG: login_view (auth_views.py) APPELÉE ---")
    
    # Sécurité : Si l'utilisateur est déjà connecté mais n'a pas d'email valide
    if request.user.is_authenticated:
        print(f"DEBUG: Utilisateur déjà connecté: {request.user.username}, Email: '{request.user.email}'")
        if not request.user.email or '@' not in request.user.email:
            print("DEBUG: Email invalide pour l'utilisateur connecté. Déconnexion forcée.")
            logout(request)
        else:
            print("DEBUG: Email valide. Redirection.")
            return redirect('MessagesAscenseurs')

    if request.method == 'POST':
        print("DEBUG: Requête POST reçue")
        
        # Cas 1: Mise à jour de l'email depuis le modal
        if 'update_email' in request.POST:
            print("DEBUG: Traitement de la mise à jour d'email")
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            
            if not email or '@' not in email:
                messages.error(request, "Email invalide.")
                return render(request, 'registration/login.html', {
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
                return redirect('MessagesAscenseurs')
            else:
                messages.error(request, "Erreur lors de la mise à jour.")
                return render(request, 'registration/login.html')
        
        # Cas 2: Tentative de connexion normale
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
            print(f"DEBUG: Tentative de connexion pour: '{username}'")
            
            users = User.objects.filter(last_name=username)
            user_found = None
            
            for u in users:
                if u.check_password(password):
                    user_found = u
                    break
            
            if user_found:
                email_actuel = user_found.email
                print(f"DEBUG: Email brut en base: '{email_actuel}'")
                
                if email_actuel:
                    email_actuel = email_actuel.strip()
                
                # Si vide, None ou pas de @ -> BLOQUER IMPERATIVEMENT
                if not email_actuel or '@' not in email_actuel:
                    print("DEBUG: >>> EMAIL INVALIDE. BLOCAGE. <<<")
                    return render(request, 'registration/login.html', {
                        'show_email_modal': True,
                        'username': username,
                        'password': password
                    })
                
                print("DEBUG: Email valide. Connexion.")
                if request.user.is_authenticated:
                    logout(request)
                    
                auth_login(request, user_found, backend='accesclient.backends.LastNameAuthBackend')
                return redirect('MessagesAscenseurs')
            else:
                messages.error(request, "Nom ou mot de passe incorrect.")
    
    return render(request, 'registration/login.html')
