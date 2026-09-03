# messages_views.py
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.core.cache import cache
from django.contrib import messages as django_messages
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from io import BytesIO
import csv
from datetime import datetime, date
import json
import os
from django.conf import settings

from ..models import MessagesAscenseurs, MessagesAscenseursDetails, ArchiveMessagesAscenseurs, Appareil
from ..forms import MessageDetailForm, MessageForm


def _get_accessible_accounts(user):
    accessible_accounts = [user.first_name]
    json_path = os.path.join(settings.BASE_DIR, 'access_config.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if user.first_name in config:
                    accessible_accounts.extend(config[user.first_name])
        except Exception as e:
            print(f"Erreur lecture JSON: {e}")
    return [acc for acc in set(accessible_accounts) if acc and acc != 'PERDU']


class MessagesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        messages = MessagesAscenseursDetails.objects.first()
        
        # 1. Liste par défaut (comportement actuel)
        accessible_accounts = [user.first_name]

        # 2. Tentative de chargement du JSON
        json_path = os.path.join(settings.BASE_DIR, 'access_config.json')
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Si l'utilisateur est dans le fichier, on étend ses droits
                    if user.first_name in config:
                        accessible_accounts.extend(config[user.first_name])
            except Exception as e:
                print(f"Erreur lecture JSON: {e}")

        accessible_accounts = [acc for acc in set(accessible_accounts) if acc and acc != 'PERDU']

        # Filter messages based on user type
        is_client = Appareil.objects.filter(Client=user.first_name).exists()
        if is_client:
            messages_list = MessagesAscenseursDetails.objects.filter(Destinataire__in=accessible_accounts)
        else:
            # For maintenance users, show messages where entretien matches OR is null/empty
            messages_list = MessagesAscenseursDetails.objects.filter(
                Q(entretien__in=accessible_accounts) |
                Q(entretien__isnull=True) |
                Q(entretien='')
            )

        # KYO ASCENSEURS-specific behavior (sort order, auto-refresh, archive
        # button) is keyed off the account itself, not the "entretien" GET
        # filter: real Destinataire is always 'KYO ASCENSEURS', while the
        # entretien field only ever holds the sub-agency ('KYO ASC 4', ...),
        # so a selected sub-agency should still count as "viewing KYO".
        is_kyo_account = is_client and 'KYO ASCENSEURS' in accessible_accounts

        # Use the accessible accounts directly so the selector matches bdd/archives behavior
        entretiens = sorted(accessible_accounts)

        # Get the selected "Entretien" from GET parameters
        selected_entretien = request.GET.get('entretien')

        # Filter messages based on selected "Entretien"
        if selected_entretien:
            messages_list = messages_list.filter(entretien=selected_entretien)

        # KYO ASCENSEURS wants to search their list by N°APP (code_client).
        napp_search = request.GET.get('napp', '').strip() if is_kyo_account else ''
        if napp_search:
            messages_list = messages_list.filter(code_client__icontains=napp_search)

        # KYO ASCENSEURS wants oldest-first ordering; everyone else keeps the
        # default most-recent-first.
        if is_kyo_account:
            messages_list = messages_list.order_by('Date')
        else:
            messages_list = messages_list.order_by('-Date')

        # Pagination
        paginator = Paginator(messages_list, 50)  # Show 50 messages per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        excluded_columns = ['Stocké', 'Incarcération', 'Opérateur', 'Confirmation', 'ConfIncar', 'ConfIncar2', 'Commentaires', 'Autres1', 'Autres2', 'Etat', 'Téléphone_2', 'N_ID', 'N_des_messages']  
        custom_column_names = {
            'entretien': 'Agence',
            'Date': 'Date du message',
            'Nature_de_l_appel': 'Type d\'appel',
            'code_client': 'N°APP',
            'Adresse': 'Adresse',
            'Code_Postal': 'Code Postal',
            'ville': 'Ville',
            'Résidence': 'Résidence',
            'Consigne_temporaire': 'Consigne Temporaire',
            'Message': 'Message',
            'Action': 'Action',
            'Nom': 'Nom',
            'Société_de_l_appelant': 'Coord. de l\'appelant',
            'Nom_de_l_appelant': 'Nom de l\'appelant',
            'Téléphone_de_l_appelant': 'Téléphone ',
            'Adresse_de_l_appelant': 'Adresse de l\'appelant',
            'Code_postal_de_l_appelant': 'Code postal de l\'appelant',
            'Ville_de_l_appelant': 'Ville de l\'appelant',
            'Observations': 'Observations',
        }

        # Nature_de_l_appel values that are routine/informational (they never
        # represent an open elevator problem) and shouldn't be flagged.
        routine_natures = {'Rapport intervention', 'Essai cabine', 'Demande renseignement'}

        # Get Résidence / Consigne Temporaire from Appareil model
        for message in page_obj:
            appareil = Appareil.objects.filter(N_ID=message.N_ID).first()
            message.Résidence = appareil.Résidence if appareil and appareil.Résidence else "--"
            # KYO ASCENSEURS wants any standing "Consigne Temporaire" on the
            # elevator (e.g. out-of-service notice) surfaced next to its messages.
            message.Consigne_temporaire = (
                appareil.Consigne_volatile
                if appareil and message.Destinataire == 'KYO ASCENSEURS' and appareil.Consigne_volatile
                else ''
            )
            # KYO ASCENSEURS wants every non-routine message flagged for as
            # long as it stays in this list: 'CLOTURE' in Action only means
            # ASTUS finished handling the call, not that the elevator issue
            # itself is fixed, so it isn't used to clear the flag. A message
            # stops being flagged only once it's archived off this list.
            message.needs_attention = bool(
                message.Destinataire == 'KYO ASCENSEURS'
                and message.Nature_de_l_appel not in routine_natures
            )
        
        selected_columns = [field_name for field_name in messages.get_fields() if request.GET.get(field_name)]

        return render(request, 'accesclient/mesasc.html', {
            'message_model': messages,
            'messages_list': page_obj,
            'page_obj': page_obj,
            'selected_columns': selected_columns,
            'excluded_columns': excluded_columns,
            'custom_column_names': custom_column_names,
            'entretiens': entretiens,
            'selected_entretien': selected_entretien,
            'is_client': is_client,
            'is_kyo_account': is_kyo_account,
            'napp_search': napp_search,
        })


class ArchiveMessagesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        # Login "astus" (the account whose Nom/last_name is "astus") gets
        # unrestricted access to every client in the archive instead of the
        # usual access_config.json-scoped list.
        has_full_client_access = (user.last_name or '').strip().lower() == 'astus'
        messages = ArchiveMessagesAscenseurs.objects.first()

        # Retrieve filter parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        selected_entretien = request.GET.get('entretien')
        search_query = request.GET.get('search', '')
        
        # Debug: print received parameters
        print(f"=== Archive Messages Filters ===")
        print(f"User: {user.first_name}")
        print(f"Start date: {start_date_str}")
        print(f"End date: {end_date_str}")
        print(f"Entretien: {selected_entretien}")
        print(f"Search: {search_query}")
        
        # 1. Get accessible accounts
        accessible_accounts = [user.first_name]
        json_path = os.path.join(settings.BASE_DIR, 'access_config.json')
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if user.first_name in config:
                        accessible_accounts.extend(config[user.first_name])
            except Exception as e:
                print(f"Erreur lecture JSON: {e}")

        # 2. Parse date range filter (computed early so the entretien dropdown
        # below can reuse it instead of scanning the full archive history)
        if start_date_str and end_date_str:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            print(f"Date filter: {start_date_str} to {end_date_str}")
        elif start_date_str:
            start_date = parse_date(start_date_str)
            end_date = timezone.now()
            print(f"Date filter: {start_date_str} to now")
        elif end_date_str:
            start_date = timezone.make_aware(datetime.datetime.min)
            end_date = parse_date(end_date_str)
            print(f"Date filter: beginning to {end_date_str}")
        else:
            # Default to the last 3 days
            start_date = timezone.now() - timezone.timedelta(days=3)
            end_date = timezone.now()
            print(f"Date filter: default 3 days")

        # 3. Get entretiens list (always needed for dropdown)
        if has_full_client_access:
            # Every distinct Client and Entretien on record (a Client such as
            # "Clauger" can have several Entretien sub-agencies, and either
            # kind of name should be pickable from the dropdown). Sourced from
            # the small Appareil master table (not the much larger archive
            # history table, which would need an unbounded full-table scan
            # for DISTINCT entretien).
            entretiens = sorted({
                e for e in list(Appareil.objects.values_list('Client', flat=True).distinct()) +
                           list(Appareil.objects.values_list('Entretien', flat=True).distinct())
                if e and e != 'PERDU'
            })
            is_client = False
        else:
            is_client = Appareil.objects.filter(Client=user.first_name).exists()
            if is_client:
                # For clients, get entretiens from messages within the current date
                # window (was unbounded over the whole archive - full table scan)
                all_messages = ArchiveMessagesAscenseurs.objects.filter(
                    Destinataire__in=accessible_accounts, Date__range=[start_date, end_date]
                )
                entretiens = list(all_messages.values_list('entretien', flat=True).distinct())
            else:
                # For maintenance users, use accessible_accounts to ensure dropdown always appears
                entretiens = sorted(list(set(accessible_accounts)))

        # 4. Fetch messages for the user based on user type
        if has_full_client_access:
            messages_list = ArchiveMessagesAscenseurs.objects.all()
        elif is_client:
            messages_list = ArchiveMessagesAscenseurs.objects.filter(Destinataire__in=accessible_accounts)
        else:
            messages_list = ArchiveMessagesAscenseurs.objects.filter(entretien__in=accessible_accounts)

        messages_list = messages_list.filter(Date__range=[start_date, end_date])
        print(f"Messages after date filter: {messages_list.count()}")

        # 5. Filter messages based on selected "Entretien"
        if selected_entretien:
            if has_full_client_access:
                # selected_entretien may be a Client name (e.g. "Clauger") that
                # covers several Entretien sub-agencies, or an Entretien name
                # directly - match messages tagged either way.
                delegated = Appareil.objects.filter(Client=selected_entretien).values_list('Entretien', flat=True).distinct()
                match_values = {selected_entretien} | {e for e in delegated if e and e != 'PERDU'}
                messages_list = messages_list.filter(Q(entretien__in=match_values) | Q(Destinataire__in=match_values))
            else:
                messages_list = messages_list.filter(entretien=selected_entretien)
            print(f"Filtering by entretien: {selected_entretien}, count: {messages_list.count()}")

        # 6. Search functionality
        if search_query:
            search_filter = Q()
            for field in ArchiveMessagesAscenseurs._meta.fields:
                search_filter |= Q(**{f"{field.name}__icontains": search_query})
            messages_list = messages_list.filter(search_filter)
            print(f"Messages after search '{search_query}': {messages_list.count()}")

        # 7. Order by date descending (most recent first)
        messages_list = messages_list.order_by('-Date')

        # 8. Pagination
        paginator = Paginator(messages_list, 150)  # Show 150 messages per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Print debugging information
        print(f"Total messages after filtering: {paginator.count}")
        print(f"Messages on current page: {page_obj.paginator.per_page}")

        excluded_columns = [
            'Stocké', 'Incarcération', 'Opérateur', 'Confirmation', 
            'ConfIncar', 'ConfIncar2', 'Commentaires', 'Autres1', 
            'Autres2', 'Etat', 'Téléphone_2', 'N_ID', 'N_des_messages',
            'Adresse', 'Code_Postal', 'ville',  # Hide these as they're combined in Résidence
        ]

        # Generate custom column names dynamically in specific order
        custom_column_names = {}
        # Add columns in desired order
        for field in ArchiveMessagesAscenseurs._meta.get_fields():
            if field.name not in excluded_columns:
                custom_column_names[field.name] = field.verbose_name
                # Insert Résidence right after Date
                if field.name == 'Date':
                    custom_column_names['Résidence'] = 'Coordonnées du Site'
        
        custom_column_names['entretien'] = 'Agence'
        selected_columns = [field.name for field in ArchiveMessagesAscenseurs._meta.get_fields() if request.GET.get(field.name)]
        
        # Combine the content to create 'Résidence' for archive messages
        # Bulk-fetch Appareils instead of one query per message (was N+1)
        page_appareil_ids = {m.N_ID for m in page_obj if m.N_ID is not None}
        page_appareils_by_id = {a.N_ID: a for a in Appareil.objects.filter(N_ID__in=page_appareil_ids)}
        for message in page_obj:
            appareil = page_appareils_by_id.get(message.N_ID)
            if appareil:
                message.Résidence = f"{message.Adresse}, {message.Code_Postal}, {message.ville}, {appareil.Résidence}"
            else:
                message.Résidence = f"{message.Adresse}, {message.Code_Postal}, {message.ville}"

        # Handle export functionality
        if 'export' in request.GET:
            # For export, use all non-excluded columns
            export_columns = [field.name for field in ArchiveMessagesAscenseurs._meta.get_fields() 
                            if field.name not in excluded_columns]
            # Add 'Résidence' and make sure 'entretien' is included
            if 'entretien' not in export_columns:
                export_columns.append('entretien')
            export_columns.append('Résidence')
            
            # Prepare messages with Résidence field
            # Bulk-fetch Appareils instead of one query per message (was N+1)
            export_list = list(messages_list)
            export_appareil_ids = {m.N_ID for m in export_list if m.N_ID is not None}
            export_appareils_by_id = {a.N_ID: a for a in Appareil.objects.filter(N_ID__in=export_appareil_ids)}
            for message in export_list:
                appareil = export_appareils_by_id.get(message.N_ID)
                if appareil:
                    message.Résidence = f"{message.Adresse}, {message.Code_Postal}, {message.ville}, {appareil.Résidence}"
                else:
                    message.Résidence = f"{message.Adresse}, {message.Code_Postal}, {message.ville}"
            
            return self.export_to_csv(export_list, export_columns, custom_column_names)

        return render(request, 'accesclient/archive_messages.html', {
            'messages': messages,
            'page_obj': page_obj,
            'messages_list': page_obj,  # Pass the paginated page object
            'selected_columns': selected_columns,
            'excluded_columns': excluded_columns,
            'custom_column_names': custom_column_names,
            'start_date': start_date_str or '',
            'end_date': end_date_str or '',
            'entretiens': entretiens,
            'selected_entretien': selected_entretien or '',
            'search_query': search_query or '',
            'has_full_client_access': has_full_client_access,
        })

    def export_to_csv(self, messages_list, export_columns, custom_column_names):
        """Export messages to Excel format instead of CSV"""
        wb = Workbook()
        ws = wb.active
        ws.title = "Archive Messages"
        
        # Write header with custom names
        headers = [custom_column_names.get(col, col) for col in export_columns]
        for col_num, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        
        # Write data rows
        for row_num, message in enumerate(messages_list, start=2):
            for col_num, col in enumerate(export_columns, start=1):
                value = getattr(message, col, None)
                
                # Handle datetime fields
                if isinstance(value, datetime):
                    if timezone.is_aware(value):
                        value = timezone.localtime(value).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        value = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, date):
                    value = value.strftime('%Y-%m-%d')
                elif value is None:
                    value = ''
                else:
                    value = str(value)
                
                ws.cell(row=row_num, column=col_num, value=value)
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="archive_messages.xlsx"'
        
        return response


def messages_list(request):
    user = request.user
    messages = MessagesAscenseursDetails.objects.filter(Destinataire=user.username)
    
    date_str = request.GET.get('date')
    if date_str:
        try:
            date_obj = parse_date(date_str)
            if date_obj:
                messages = messages.filter(Date__date=date_obj)
        except ValueError:
            pass
    
    return render(request, 'accesclient/messages_list.html', {'messages': messages})


def message_detail(request, pk):
    message = get_object_or_404(MessagesAscenseursDetails, pk=pk)
    
    if request.method == 'POST':
        form = MessageDetailForm(request.POST)
        if form.is_valid():
            fields = [field for field, value in form.cleaned_data.items() if value]
    else:
        form = MessageDetailForm()
        fields = [field.verbose_name for field in MessagesAscenseursDetails._meta.get_fields() if field.name != 'N_des_messages']

    return render(request, 'accesclient/message_detail.html', {'message': message, 'form': form, 'fields': fields})


def create_message(request, N_ID):
    appareil = get_object_or_404(Appareil, N_ID=N_ID)
    code_client = appareil.Code_Client
    destinataire = appareil.Destinataire

    if request.method == 'POST':
        form = MessageForm(request.POST, user=request.user)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            MessagesAscenseurs.objects.create(
                Nature_de_l_appel=cleaned_data['Nature_de_l_appel'],
                Nom_de_l_appelant=cleaned_data['Nom_de_l_appelant'],
                Société_de_l_appelant=cleaned_data['Société_de_l_appelant'],
                Téléphone_de_l_appelant=cleaned_data['Téléphone_de_l_appelant'],
                Message=cleaned_data['Message'],
                Destinataire=destinataire,
                N_ID=N_ID  # Use the N_ID from URL parameter directly
            )
            return redirect('appareil_list')  
    else:
        # Initialize form with N_ID value
        form = MessageForm(user=request.user, initial={'N_ID': N_ID})

    return render(request, 'accesclient/create_message.html', {
        'form': form,
        'code_client': code_client,
        'destinataire': destinataire,
    })


def export_messages_to_excel(request):
    user = request.user
    
    # 1. Liste par défaut (comportement actuel)
    accessible_accounts = [user.first_name]

    # 2. Tentative de chargement du JSON
    json_path = os.path.join(settings.BASE_DIR, 'access_config.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if user.first_name in config:
                    accessible_accounts.extend(config[user.first_name])
        except Exception:
            pass

    # Filter messages based on user type using MessagesAscenseursDetails to get 'entretien'
    is_client = Appareil.objects.filter(Client=user.first_name).exists()
    if is_client:
        messages = MessagesAscenseursDetails.objects.filter(Destinataire__in=accessible_accounts)
    else:
        messages = MessagesAscenseursDetails.objects.filter(entretien__in=accessible_accounts)

    # Apply Entretien filter if present
    selected_entretien = request.GET.get('entretien')
    if selected_entretien:
        messages = messages.filter(entretien=selected_entretien)

    wb = Workbook()
    ws = wb.active
    ws.title = "Messages"

    # Define headers for the Excel file
    headers = [
        'Destinataire',
        'Date',
        'Message',
        'Nom',
        'Téléphone',
        'Digicode',
        'Action',
        'Société de l\'appelant',
        'Nom de l\'appelant',
        'Adresse de l\'appelant',
        'Code postal de l\'appelant',
        'Ville de l\'appelant',
        'Téléphone de l\'appelant',
        'Digicode de l\'appelant',
        'Nature de l\'appel',
        'Agence' # Added Agence column
    ]

    # Write headers to the first row in the worksheet
    for col_num, header in enumerate(headers, 1):
        ws.cell(row=1, column=col_num, value=header)

    # Write data rows
    for row_num, message in enumerate(messages, 2):  # Start from row 2 for data
        ws.cell(row=row_num, column=1, value=message.Destinataire)
        # Handle datetime - check if it's timezone-aware or naive
        if message.Date:
            if timezone.is_aware(message.Date):
                local_date = timezone.localtime(message.Date)
                ws.cell(row=row_num, column=2, value=local_date.replace(tzinfo=None))
            else:
                # Naive datetime - use as-is
                ws.cell(row=row_num, column=2, value=message.Date)
        else:
            ws.cell(row=row_num, column=2, value="")
            
        ws.cell(row=row_num, column=3, value=message.Message)
        ws.cell(row=row_num, column=4, value=message.Nom)
        ws.cell(row=row_num, column=5, value=message.Téléphone)
        ws.cell(row=row_num, column=6, value=message.Digicode)
        ws.cell(row=row_num, column=7, value=message.Action)
        ws.cell(row=row_num, column=8, value=message.Société_de_l_appelant)
        ws.cell(row=row_num, column=9, value=message.Nom_de_l_appelant)
        ws.cell(row=row_num, column=10, value=message.Adresse_de_l_appelant)
        ws.cell(row=row_num, column=11, value=message.Code_postal_de_l_appelant)
        ws.cell(row=row_num, column=12, value=message.Ville_de_l_appelant)
        ws.cell(row=row_num, column=13, value=message.Téléphone_de_l_appelant)
        ws.cell(row=row_num, column=14, value=message.Digicode_de_l_appelant)
        ws.cell(row=row_num, column=15, value=message.Nature_de_l_appel)
        ws.cell(row=row_num, column=16, value=message.entretien) # Added Agence value

    filename = f"messages_{user.username}.xlsx"

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)

    return response


@login_required
@require_http_methods(["POST"])
def archive_messages(request):
    """Archive the resolved messages of one account (e.g. 'KYO ASCENSEURS'):
    move them from MessagesAscenseurs into ArchiveMessagesAscenseurs and
    remove them from the working list, mirroring the old "Archiver" button.
    """
    destinataire = request.POST.get('destinataire', '').strip()
    accessible_accounts = _get_accessible_accounts(request.user)

    is_client = Appareil.objects.filter(Client=request.user.first_name).exists()
    if not is_client or not destinataire or destinataire not in accessible_accounts:
        django_messages.error(request, "Vous n'avez pas accès à ce compte.")
        return redirect(reverse('MessagesAscenseurs'))

    # A message is considered resolved (archivable) unless it still needs
    # follow-up (attention/incarcération/panne/dysfonctionnement) and hasn't
    # been marked OK, or it's still awaiting confirmation/stock/sonnette handling.
    needs_follow_up = (
        Q(Nature_de_l_appel__iendswith='ention')
        | Q(Nature_de_l_appel__iendswith='arceration')
        | Q(Nature_de_l_appel__iendswith='anne')
        | Q(Nature_de_l_appel__iendswith='nctionnement')
    )

    candidates = MessagesAscenseurs.objects.filter(
        Destinataire=destinataire,
        ConfIncar__isnull=True,
    ).exclude(
        Action__istartswith='Stock'
    ).exclude(
        Action__istartswith='Sonn'
    ).filter(~needs_follow_up | Q(Autres2='OK'))

    with transaction.atomic():
        rows = list(candidates)
        if rows:
            ArchiveMessagesAscenseurs.objects.bulk_create([
                ArchiveMessagesAscenseurs(
                    N_des_messages=r.N_des_messages,
                    N_ID=r.N_ID,
                    Destinataire=r.Destinataire,
                    Date=r.Date,
                    Message=r.Message,
                    Nom=r.Nom,
                    Téléphone=r.Téléphone,
                    Digicode=r.Digicode,
                    Action=r.Action,
                    Nom_de_l_appelant=r.Nom_de_l_appelant,
                    Société_de_l_appelant=r.Société_de_l_appelant,
                    Adresse_de_l_appelant=r.Adresse_de_l_appelant,
                    Code_postal_de_l_appelant=r.Code_postal_de_l_appelant,
                    Ville_de_l_appelant=r.Ville_de_l_appelant,
                    Téléphone_de_l_appelant=r.Téléphone_de_l_appelant,
                    Digicode_de_l_appelant=r.Digicode_de_l_appelant,
                    Nature_de_l_appel=r.Nature_de_l_appel,
                    Stocké=r.Stocké,
                    Incarcération=r.Incarcération,
                    Opérateur=r.Opérateur,
                    Téléphone_2=r.Téléphone_2,
                    Confirmation=r.Confirmation,
                    ConfIncar=r.ConfIncar,
                    ConfIncar2=r.ConfIncar2,
                    Commentaires=r.Commentaires,
                    Autres1=r.Autres1,
                    Autres2=r.Autres2,
                    Etat=r.Etat,
                ) for r in rows
            ])
            MessagesAscenseurs.objects.filter(
                N_des_messages__in=[r.N_des_messages for r in rows]
            ).delete()

    if rows:
        django_messages.success(request, f"{len(rows)} message(s) archivé(s) pour {destinataire}.")
    else:
        django_messages.info(request, f"Aucun message à archiver pour {destinataire}.")

    return redirect(f"{reverse('MessagesAscenseurs')}?entretien={destinataire}")
