# forms.py
import re
import pandas as pd
from django import forms
from datetime import datetime
from django.utils import timezone
from .models import MessagesAscenseurs , ArchiveMessagesAscenseurs , Appareil , Astreinte , Repertoire, Alerte
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import connection
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm

class ExcelUploadForm(forms.Form):
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label="Upload Excel File"
    )
class ColumnSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ColumnSelectionForm, self).__init__(*args, **kwargs)
        model_fields = MessagesAscenseurs._meta.fields
        for field in model_fields:
            self.fields[field.name] = forms.BooleanField(label=field.verbose_name, required=False)
class MessageDetailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(MessageDetailForm, self).__init__(*args, **kwargs)
        model_fields = MessagesAscenseurs._meta.get_fields()
        choices = [(field.name, field.verbose_name) for field in model_fields if field.name != 'N_des_messages']
        self.fields['fields'] = forms.MultipleChoiceField(choices=choices, widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '10'}), required=False)

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class MessageForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(MessageForm, self).__init__(*args, **kwargs)
        # Initialize Nature_de_l_appel field regardless of user context
        self.fields['Nature_de_l_appel'] = forms.ChoiceField(
            label="Nature de l'appel",
            choices=self.get_nature_de_l_appel_choices(user),
            required=True
        )

    def get_nature_de_l_appel_choices(self, user):
        if user is None:
            return []
        
        # Apply the same conditional logic as in views
        if user.is_superuser:
            choices = ArchiveMessagesAscenseurs.objects.filter(
                Destinataire=user.username
            ).values_list('Nature_de_l_appel', flat=True).distinct()
        else:
            choices = ArchiveMessagesAscenseurs.objects.filter(
                entretien=user.first_name
            ).values_list('Nature_de_l_appel', flat=True).distinct()
        
        # Exclude 'Essai cabine' and choices starting with 'Relance'
        filtered_choices = [
            choice for choice in choices
            if choice != 'Essai cabine' and not choice.startswith('Relance')
        ]
      
        sorted_choices = sorted(set(filtered_choices))
        return [(choice, choice) for choice in sorted_choices]

    Nom_de_l_appelant = forms.CharField(label="Nom de l'appelant", max_length=100)
    Société_de_l_appelant = forms.CharField(label="Société de l'appelant", max_length=100)
    Téléphone_de_l_appelant = forms.CharField(label="Téléphone de l'appelant", max_length=15)
    Message = forms.CharField(label='Message', widget=forms.Textarea)
    N_ID = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    

class AppareilModificationForm(forms.ModelForm):
    Client = forms.ChoiceField(choices=[], required=True)
    Entretien = forms.ChoiceField(choices=[], required=True)
    Destinataire = forms.ChoiceField(choices=[], required=True)
    Type = forms.ChoiceField(choices=[], required=False)
    Code_Client = forms.CharField(required=True)
    Adresse = forms.CharField(required=True)
    Code_Postal = forms.CharField(required=True)
    Ville = forms.CharField(required=True)
    Résidence = forms.CharField(required=True)
    
    def __init__(self, *args, **kwargs):
        clients = kwargs.pop('clients', [])
        entretiens = kwargs.pop('entretiens', [])
        types = kwargs.pop('types', [])
        super().__init__(*args, **kwargs)
        
        if clients:
            self.fields['Client'].choices = [(c, c) for c in clients]
        if entretiens:
            self.fields['Entretien'].choices = [(e, e) for e in entretiens]
            self.fields['Destinataire'].choices = [(e, e) for e in entretiens]
        if types:
            self.fields['Type'].choices = [('', '-- Sélectionner un type --')] + [(t, t) for t in types]
        
        # Make other fields optional
        optional_fields = ['Informations', 'Incarcération', 'Type', 'Phonie', 'Transmetteur', 'Observations', 'Consigne_volatile', 'MES', 'RES']
        for field_name in optional_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False
    
    class Meta:
        model = Appareil
        fields = ['Client', 'Entretien', 'Destinataire', 'Code_Client', 'Adresse', 'Code_Postal','Ville','Résidence','Informations','Incarcération','Type','Phonie','Transmetteur','Observations','Consigne_volatile','MES','RES']  

def validate_phone(value):
    """Validate that the value is a 10-digit phone number starting with 0."""
    phone_pattern = r'^0\d{9}$'
    if not re.match(phone_pattern, value):
        raise ValidationError("Enter a valid 10-digit phone number starting with 0.")


def validate_email(value):
    """Validate that the value is a valid email address."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, value):
        raise ValidationError("Enter a valid email address.")


class AstreinteForm(forms.ModelForm):
    TYPE_CHOICES = [
        ('Telephone', 'Telephone'),
        ('Email', 'Email'),
    ]

    
    date_debut = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    heure_debut = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    date_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    heure_fin = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    priorite = forms.ChoiceField(
        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4")],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    detail_astreinte = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False
    )

   
    type1 = forms.ChoiceField(choices=TYPE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    media1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    type2 = forms.ChoiceField(choices=TYPE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    media2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    type3 = forms.ChoiceField(choices=TYPE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    media3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    type4 = forms.ChoiceField(choices=TYPE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    media4 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    entretien = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label="Entretien"
    )
    technician = forms.ModelChoiceField(
        queryset=Repertoire.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label="Repertoire"
    )       
    class Meta:
        model = Astreinte
        fields = [
            'entretien', 'date_debut', 'heure_debut', 'date_fin', 'heure_fin',
            'priorite', 'detail_astreinte',
            'type1', 'media1', 'type2', 'media2',
            'type3', 'media3', 'type4', 'media4'
        ]
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Safely get user from kwargs
        super().__init__(*args, **kwargs)

        # Populate entretien choices based on user access
        if user:
            from django.db.models import Q
            import os
            import json
            from django.conf import settings
            
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

            # Remove duplicates and sort
            accessible_users = sorted(list(set(accessible_users)))

            # Create choices directly from accessible users
            entretien_choices = [(e, e) for e in accessible_users]
            
            self.fields['entretien'].choices = entretien_choices

        if self.instance and self.instance.pk:
            if self.instance.date_debut:
                local_dt = timezone.localtime(self.instance.date_debut)
                self.initial['date_debut'] = local_dt.strftime('%Y-%m-%d')
                self.initial['heure_debut'] = local_dt.strftime('%H:%M')
            if self.instance.date_fin:
                local_dt = timezone.localtime(self.instance.date_fin)
                self.initial['date_fin'] = local_dt.strftime('%Y-%m-%d')
                self.initial['heure_fin'] = local_dt.strftime('%H:%M')

        if user:
            # Filter technicians based on the logged-in user's client
            filtered_technicians = Repertoire.objects.filter(client=user.username)
            print("Filtered Technicians Queryset:", filtered_technicians)  # Print queryset to debug
            self.fields['technician'].queryset = filtered_technicians

    def clean(self):
        cleaned_data = super().clean()
        
        # Use Paris timezone explicitly to avoid server timezone issues
        import pytz
        paris_tz = pytz.timezone('Europe/Paris')
        
        # Combine date and time for date_debut
        date_debut = cleaned_data.get('date_debut')
        heure_debut = cleaned_data.get('heure_debut')
        if date_debut and heure_debut:
            # Create a naive datetime
            dt = datetime.combine(date_debut, heure_debut)
            # Make it aware in Paris timezone explicitly
            cleaned_data['date_debut'] = paris_tz.localize(dt)
            
        # Combine date and time for date_fin
        date_fin = cleaned_data.get('date_fin')
        heure_fin = cleaned_data.get('heure_fin')
        if date_fin and heure_fin:
            # Create a naive datetime
            dt = datetime.combine(date_fin, heure_fin)
            # Make it aware in Paris timezone explicitly
            cleaned_data['date_fin'] = paris_tz.localize(dt)

        
        for i in range(1, 5):
            type_field = cleaned_data.get(f"type{i}")
            media_field = cleaned_data.get(f"media{i}")

            if type_field and media_field:
                if type_field == 'Telephone':
                    try:
                        cleaned_data[f"media{i}"] = validate_phone(media_field)
                    except ValidationError as e:
                        self.add_error(f'media{i}', f"Numéro de téléphone invalide : {e.message}")
                elif type_field == 'Email':
                    if not validate_email(media_field):
                        self.add_error(f'media{i}', f"Format d'email invalide : {media_field}. Veuillez entrer une adresse email valide.")

        return cleaned_data
    
def validate_email(email):
    
    if isinstance(email, str):
        
        if re.match(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$', email):
            return True
        else:
            return False
    return False  
def validate_phone(phone_number):
    
    phone_number = str(phone_number).strip()

    # If it's a 9-digit number not starting with '0', prepend '0'
    if len(phone_number) == 9 and not phone_number.startswith('0'):
        phone_number = '0' + phone_number  
    
    print(f"Phone number before validation: {phone_number}")  

    # Check if the number starts with '0' or '+' and normalize it
    if phone_number.startswith('0') or phone_number.startswith('+'):
        # Normalize by keeping '+' at the start and removing all non-digits after
        if phone_number.startswith('+'):
            phone_number_normalized = '+' + re.sub(r'\D', '', phone_number[1:])
        else:
            phone_number_normalized = re.sub(r'\D', '', phone_number)

        # Validate length (10-15 digits)
        if 10 <= len(phone_number_normalized.lstrip('+')) <= 15:
            return phone_number_normalized

    # Raise error if validation fails
    raise ValidationError(
        f"Le numéro de téléphone est incorrect : {phone_number}. "
        f"Veuillez entrer un numéro valide de 10 à 15 chiffres, commençant par '0' ou '+'."
    )

def process_excel_file(file, created_by):
    error_messages = []  

    try:
        
        df = pd.read_excel(file)
        print(f"Excel file read successfully. {len(df)} rows found.")  # Debug line

        
        required_columns = [
            "Client", "dateDebut", "dateFin", "priorite", "detailAstreinte",
            "type1", "media1", "type2", "media2", "type3", "media3", "type4", "media4", "Créé par"
        ]

       
        if not all(col in df.columns for col in required_columns):
            raise ValidationError("Le fichier Excel téléchargé ne possède pas toutes les colonnes requises.")
        
        print("Column validation passed.")  # Debug line
        df = df.applymap(lambda x: "" if pd.isna(x) else x)
        
        for index, row in df.iterrows():
            print(f"Processing row {index + 1}: {row['Client']}")  
            
            
            priorite = row['priorite']
            if priorite not in [1, 2, 3, 4]:
                error_messages.append(f"Valeur prioritaire invalide à la ligne {index + 1}: {priorite}")

            
            for i in range(1, 5):
                type_field = row.get(f"type{i}")
                media_field = row.get(f"media{i}")

                
                if pd.isna(type_field) and pd.isna(media_field):
                    continue 

              
                if pd.isna(type_field) or pd.isna(media_field):
                    error_messages.append(f"Ligne {index + 1} manque type{i} ou media{i}.")
                    continue  

                
                if type_field and media_field:
                    if type_field == "Telephone":
                       
                        media_field = validate_phone(media_field)  
                        if not validate_phone(media_field):
                            error_messages.append(f"Le format du numéro de téléphone est incorrect à la ligne {index + 1}, type{i}: {media_field}. Veuillez entrer un numéro valide de 10 chiffres commençant par 0, sans espaces ni caractères spéciaux.")
                    elif type_field == "Email":
                        if not validate_email(str(media_field)): 
                            error_messages.append(f"Le format de l'email n'est pas respecté à la ligne {index + 1}, type{i}: {media_field}.")
                    else:
                        error_messages.append(f"Type '{type_field}' invalide à la ligne {index + 1}, type{i}. Les types acceptés sont uniquement 'Telephone' ou 'Email' (respectez les majuscules).")

            # Parse and convert date formats
            try:
                date_debut = row["dateDebut"]
                if isinstance(date_debut, str):
                    # Try multiple date formats
                    for date_format in ["%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]:
                        try:
                            date_debut = datetime.strptime(date_debut, date_format)
                            break
                        except ValueError:
                            continue
                    else:
                        error_messages.append(f"Format de date invalide pour dateDebut à la ligne {index + 1}. Utilisez le format JJ/MM/AAAA HH:MM ou AAAA-MM-JJ HH:MM.")
                        continue
                elif hasattr(date_debut, 'to_pydatetime'):
                    # If it's a pandas Timestamp, convert to datetime (naive, no timezone)
                    date_debut = date_debut.to_pydatetime()
                    # Remove timezone info if present to keep as naive datetime
                    if timezone.is_aware(date_debut):
                        date_debut = date_debut.replace(tzinfo=None)
                
                date_fin = row["dateFin"]
                if isinstance(date_fin, str):
                    # Try multiple date formats
                    for date_format in ["%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]:
                        try:
                            date_fin = datetime.strptime(date_fin, date_format)
                            break
                        except ValueError:
                            continue
                    else:
                        error_messages.append(f"Format de date invalide pour dateFin à la ligne {index + 1}. Utilisez le format JJ/MM/AAAA HH:MM ou AAAA-MM-JJ HH:MM.")
                        continue
                elif hasattr(date_fin, 'to_pydatetime'):
                    # If it's a pandas Timestamp, convert to datetime (naive, no timezone)
                    date_fin = date_fin.to_pydatetime()
                    # Remove timezone info if present to keep as naive datetime
                    if timezone.is_aware(date_fin):
                        date_fin = date_fin.replace(tzinfo=None)
                    
            except Exception as e:
                error_messages.append(f"Erreur lors du traitement des dates à la ligne {index + 1}: {str(e)}")
                continue
            
            if not error_messages:
                Astreinte.objects.create(
                    entretien=row["Client"],
                    date_debut=date_debut,
                    date_fin=date_fin,
                    priorite=row["priorite"],
                    detail_astreinte=row.get("detailAstreinte", ""),
                    type1=row.get("type1"),
                    media1=row.get("media1"),
                    type2=row.get("type2"),
                    media2=row.get("media2"),
                    type3=row.get("type3"),
                    media3=row.get("media3"),
                    type4=row.get("type4"),
                    media4=row.get("media4"),
                    operator_create=created_by,
                    date_import=timezone.now()
                )

        if error_messages:
            return error_messages  
        return True

    except ValidationError as e:
        return [str(e)]  
    except Exception as e:
        return [f"Une erreur s'est produite : {str(e)}"]  
class TechnicianForm(forms.ModelForm):
    class Meta:
        model = Repertoire
        fields = ['nom_technicien', 'client']
class RepertoireForm(forms.ModelForm):
    class Meta:
        model = Repertoire
        fields = ['client', 'nom_technicien', 'type1', 'media1', 'type2', 'media2', 'type3', 'media3', 'type4', 'media4']

class LastNameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom",
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Nom de famille'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nom de famille'


class AlerteForm(forms.ModelForm):
    class Meta:
        model = Alerte
        fields = ['jour', 'heure', 'email', 'agence', 'date_surveiller']
        widgets = {
            'jour': forms.Select(attrs={'class': 'form-control'}),
            'heure': forms.TextInput(attrs={'class': 'form-control', 'type': 'time', 'placeholder': 'HH:MM'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email1@exemple.com, email2@exemple.com'}),
            'agence': forms.TextInput(attrs={'class': 'form-control'}),
            'date_surveiller': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].help_text = 'Séparez plusieurs emails par des virgules'
        self.fields['date_surveiller'].help_text = 'Nombre de jours à partir de la date actuelle'
        self.fields['jour'].required = True
        self.fields['heure'].required = True
        self.fields['email'].required = True
        self.fields['agence'].required = True