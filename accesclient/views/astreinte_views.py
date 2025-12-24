# astreinte_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q, Case, When, Value, BooleanField
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
import json
import os
from django.conf import settings

from ..models import Astreinte, Appareil
from ..forms import AstreinteForm, ExcelUploadForm, process_excel_file


def create_astreinte(request):
    if request.method == 'POST':
        form = AstreinteForm(request.POST, user=request.user)  # Pass the user here
        if form.is_valid():
            astreinte = form.save(commit=False)
            astreinte.operator_create = request.user.username
            astreinte.entretien = request.user.username
            astreinte.technician = form.cleaned_data['technician']
            astreinte.save()
            return redirect('http://127.0.0.1:8000/create-astreinte/')
    else:
        form = AstreinteForm(user=request.user)

    return render(request, 'Astreinte/astreinte_form.html', {'form': form})


def upload_excel(request):
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data['file']
            created_by = request.user.username  
            result = process_excel_file(excel_file, created_by)

            if result is True:
                messages.success(request, "Fichier traité et données insérées avec succès !")
            else:
                # If result is a list of errors, display them
                for error in result:
                    messages.error(request, error)
            return redirect("upload_excel")
    else:
        form = ExcelUploadForm()

    return render(request, "Astreinte/upload_excel.html", {"form": form})


def view_astreintes(request):
    user = request.user
    sort_order = request.GET.get('sort', 'date_debut')
    search_query = request.GET.get('q', '')
    filter_date = request.GET.get('filter_date', '')
    selected_entretien = request.GET.get('entretien', '')



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

    prefix_filters = Q()
    if len(accessible_users) == 1 and accessible_users[0] == user.first_name:
        # Single user case - use exact match instead of startswith
        prefix_filters = Q(entretien=user.first_name)
    else:
        # Multiple users case - use startswith logic
        for username in accessible_users:
            prefix_filters |= Q(entretien__startswith=username)

    available_entretiens = list(Astreinte.objects.filter(
        prefix_filters
    ).values_list('entretien', flat=True).distinct().order_by('entretien'))

    base_entretien = next((e for e in available_entretiens if e == user.username), None)
    if not selected_entretien:
        selected_entretien = base_entretien or (available_entretiens[0] if available_entretiens else None)

    filters = prefix_filters

    if selected_entretien:
        filters &= Q(entretien=selected_entretien)

    # Check if user is applying any specific search or date filter
    has_search_filter = bool(search_query)
    has_date_filter = bool(filter_date)
    view_all = request.GET.get('view_all') == 'true'

    if not has_search_filter and not has_date_filter and not view_all:
        # Default view: Show currently active astreintes (by day and hour)
        now = timezone.now()
        filters &= Q(date_debut__lte=now) & Q(date_fin__gte=now)
        
        # Default sort to priority if not explicitly set by user
        if 'sort' not in request.GET:
            sort_order = 'priorite'

    if has_search_filter:
        try:
            search_date = datetime.strptime(search_query, '%Y-%m-%d')
            filters &= Q(date_debut__lte=search_date) & Q(date_fin__gte=search_date)
        except ValueError:
            search_filters = (
                Q(detail_astreinte__icontains=search_query) |
                Q(operator_create__icontains=search_query) |
                Q(media1__icontains=search_query) |
                Q(media2__icontains=search_query) |
                Q(media3__icontains=search_query) |
                Q(media4__icontains=search_query)
            )
            filters &= search_filters

    if has_date_filter:
        try:
            filter_date_parsed = datetime.strptime(filter_date, '%Y-%m-%d')
            filters &= Q(date_debut__lte=filter_date_parsed + timedelta(days=1)) & Q(date_fin__gte=filter_date_parsed)
        except ValueError:
            pass

    astreintes = Astreinte.objects.filter(filters).order_by(sort_order)

    return render(request, 'Astreinte/view_astreintes.html', {
        'astreintes': astreintes,
        'sort_order': sort_order,
        'search_query': search_query,
        'filter_date': filter_date,
        'selected_entretien': selected_entretien,
        'available_entretiens': available_entretiens,
        'view_all': view_all,
    })


def delete_astreinte(request, id_astreinte):
    astreinte = get_object_or_404(Astreinte, id_astreinte=id_astreinte)
    astreinte.delete()
    messages.success(request, "L'astreinte a été supprimée avec succès.")
    return redirect(reverse('view_astreintes'))


def modify_astreinte(request, id_astreinte):
    astreinte = get_object_or_404(Astreinte, id_astreinte=id_astreinte)

    if request.method == 'POST':
        form = AstreinteForm(request.POST, instance=astreinte, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "L'astreinte a été modifiée avec succès.")
            return redirect(reverse('view_astreintes'))
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = AstreinteForm(instance=astreinte, user=request.user)

    return render(request, 'Astreinte/modify_astreinte.html', {'form': form, 'astreinte': astreinte})
