# consigne_views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import os
import json
from django.conf import settings

from ..models import Consigne, Appareil


@login_required
def view_consignes(request):
    user = request.user

    # Get delegated users dynamically from Appareil model based on user type
    if Appareil.objects.filter(Client=user.first_name).exists():
        # User exists as Client - get all distinct entretiens from Appareil
        delegated_users = list(Appareil.objects.filter(
            Client=user.first_name
        ).values_list('Entretien', flat=True).distinct())
        
        # Remove None values and add current user
        delegated_users = [entretien for entretien in delegated_users if entretien]
        accessible_users = [user.username] + delegated_users
    else:
        # User doesn't exist as Client - only use user.first_name
        accessible_users = [user.first_name]

    # Load additional access from JSON config
    json_path = os.path.join(settings.BASE_DIR, 'access_config.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if user.first_name in config:
                    accessible_users.extend(config[user.first_name])
        except Exception as e:
            print(f"Erreur lecture JSON: {e}")

    # Build filter for accessible consignes
    prefix_filters = Q()
    if len(accessible_users) == 1 and accessible_users[0] == user.first_name:
        # Single user case - use exact match instead of startswith
        prefix_filters = Q(Client=user.first_name)
    else:
        # Multiple users case - use startswith logic
        for username in accessible_users:
            prefix_filters |= Q(Client__startswith=username)

    # Filter consignes based on user access
    consignes = Consigne.objects.filter(prefix_filters)

    # Order by Client name
    consignes = consignes.order_by('Client')

    context = {
        'consignes': consignes,
        'user': user,
    }

    return render(request, 'accesclient/consignes_list.html', context)
