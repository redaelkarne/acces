# forms.py
import re
import pandas as pd
from django import forms
from datetime import datetime
from django.utils import timezone
from .models import MessagesAscenseurs , ArchiveMessagesAscenseurs , Appareil , Astreinte , Repertoire
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
    class Meta:
        model = Appareil
        fields = ['Code_Client', 'Adresse', 'Code_Postal','Ville','Résidence','Informations','Incarcération','Type','Phonie','Transmetteur','Observations','Consigne_volatile','MES','RES']  

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

    technician = forms.ModelChoiceField(
        queryset=Repertoire.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label="Repertoire"
    )       
    class Meta:
        model = Astreinte
        fields = [
            'date_debut', 'heure_debut', 'date_fin', 'heure_fin',
            'priorite', 'detail_astreinte',
            'type1', 'media1', 'type2', 'media2',
            'type3', 'media3', 'type4', 'media4'
        ]
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Safely get user from kwargs
        super().__init__(*args, **kwargs)

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
        
        # Combine date and time for date_debut
        date_debut = cleaned_data.get('date_debut')
        heure_debut = cleaned_data.get('heure_debut')
        if date_debut and heure_debut:
            dt = datetime.combine(date_debut, heure_debut)
            cleaned_data['date_debut'] = timezone.make_aware(dt)
            
        # Combine date and time for date_fin
        date_fin = cleaned_data.get('date_fin')
        heure_fin = cleaned_data.get('heure_fin')
        if date_fin and heure_fin:
            dt = datetime.combine(date_fin, heure_fin)
            cleaned_data['date_fin'] = timezone.make_aware(dt)

        
        for i in range(1, 5):
            type_field = cleaned_data.get(f"type{i}")
            media_field = cleaned_data.get(f"media{i}")

            if type_field and media_field:
                if type_field == 'Telephone':
                    validate_phone(media_field)
                elif type_field == 'Email':
                    validate_email(media_field)

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
                        error_messages.append(f"Type '{type_field}' invalide à la ligne {index + 1}, type{i}.")

            
            if not error_messages:
                Astreinte.objects.create(
                    entretien=row["Client"],
                    date_debut=row["dateDebut"],
                    date_fin=row["dateFin"],
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
                    date_import=datetime.now()
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