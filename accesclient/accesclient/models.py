from django.db import models
from django.contrib.auth.models import User

class MessagesAscenseurs(models.Model):
    
    N_des_messages = models.AutoField(primary_key=True, verbose_name='N°des messages')
    N_ID = models.IntegerField(null=True, blank=True, verbose_name='N° ID')
    Destinataire = models.CharField(max_length=255, null=True, blank=True)
    Date = models.DateTimeField(null=True, blank=True)
    Message = models.TextField(null=True, blank=True)
    Nom = models.CharField(max_length=255, null=True, blank=True)
    Téléphone = models.CharField(max_length=255, null=True, blank=True)
    Digicode = models.CharField(max_length=255, null=True, blank=True)
    Action = models.TextField(null=True, blank=True)
    Nom_de_l_appelant = models.CharField(max_length=255, null=True, blank=True, verbose_name='Nom de l\'appelant')
    Société_de_l_appelant = models.CharField(max_length=255, null=True, blank=True, verbose_name='Société de l\'appelant')
    Adresse_de_l_appelant = models.CharField(max_length=255, null=True, blank=True, verbose_name='Adresse de l\'appelant')
    Code_postal_de_l_appelant = models.CharField(max_length=255, null=True, blank=True, verbose_name='Code postal de l\'appelant')
    Ville_de_l_appelant = models.CharField(max_length=255, null=True, blank=True, verbose_name='Ville de l\'appelant')
    Téléphone_de_l_appelant = models.CharField(max_length=255, null=True, blank=True, verbose_name='Téléphone de l\'appelant')
    Digicode_de_l_appelant = models.CharField(max_length=255, null=True, blank=True, verbose_name='Digicode de l\'appelant')
    Nature_de_l_appel = models.CharField(max_length=255, null=True, blank=True, verbose_name='Nature de l\'appel')
    Stocké = models.CharField(max_length=255, null=True, blank=True)
    Incarcération = models.CharField(max_length=255, null=True, blank=True)
    Opérateur = models.CharField(max_length=255, null=True, blank=True)
    Téléphone_2 = models.CharField(max_length=255, null=True, blank=True, verbose_name='Téléphone 2')
    Confirmation = models.CharField(max_length=255, null=True, blank=True)
    ConfIncar = models.DateTimeField(null=True, blank=True)
    ConfIncar2 = models.CharField(max_length=255, null=True, blank=True)
    Commentaires = models.TextField(null=True, blank=True)
    Autres1 = models.CharField(max_length=255, null=True, blank=True)
    Autres2 = models.CharField(max_length=255, null=True, blank=True)
    Etat = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        db_table = 'view_messages_ascenseurs'
        verbose_name = 'Message Ascenseur'
        verbose_name_plural = 'Messages Ascenseurs'

    def get_fields(self):
         return [field.name for field in self._meta.get_fields()]
    
    def __iter__(self):
        for field in self._meta.fields:
            yield (field.verbose_name, field.value_to_string(self))

class Appareil(models.Model):
    s_Generation = models.IntegerField(null=True, blank=True)
    s_GUID = models.CharField(max_length=38, null=True, blank=True, unique=True)
    s_Lineage = models.BinaryField(null=True, blank=True)
    N_ID = models.AutoField(primary_key=True, verbose_name='N° ID')
    DateCreation = models.DateTimeField(auto_now_add=True, null=True)
    Client = models.CharField(max_length=50)
    Opérateur = models.CharField(max_length=50, null=True, blank=True, default='Importé')
    Entretien = models.CharField(max_length=50)
    Destinataire = models.CharField(max_length=50)
    Télésurveillance = models.CharField(max_length=50, null=True, blank=True)
    Adresse = models.CharField(max_length=255, default=' ')
    Code_Postal = models.CharField(max_length=10, null=True, blank=True, verbose_name='Code Postal')
    Ville = models.CharField(max_length=100, null=True, blank=True)
    Résidence = models.CharField(max_length=200, default=' ')
    Informations = models.CharField(max_length=150, default=' ')
    Code_Client = models.CharField(max_length=50, default=' ')
    Type = models.CharField(max_length=25, null=True, blank=True, default='DEFAULT VALUE')
    MaJFacture = models.BooleanField(default=False)
    Incarcération = models.CharField(max_length=50, null=True, blank=True)
    Code_consigne = models.CharField(max_length=50, null=True, blank=True, verbose_name='Code consigne')
    Consigne_volatile = models.CharField(max_length=255, null=True, blank=True, verbose_name='Consigne volatile')
    Utilisateur = models.CharField(max_length=50, null=True, blank=True)
    Opérateur2 = models.CharField(max_length=50, null=True, blank=True)
    dateImport = models.DateTimeField(auto_now_add=True, null=True)
    MES = models.DateTimeField(null=True, blank=True)
    RES = models.DateTimeField(null=True, blank=True)
    Phonie = models.CharField(max_length=50, default=' ')
    Transmetteur = models.CharField(max_length=200, default=' ')
    Autres_1 = models.TextField(null=True, blank=True)
    Autres_2 = models.TextField(null=True, blank=True)
    Observations = models.CharField(max_length=2048, null=True, blank=True)
    Id_Societe = models.IntegerField(null=True, blank=True)

    def get_fields(self):
         return [field.name for field in self._meta.get_fields()]
    
    def __iter__(self):
        for field in self._meta.fields:
            yield (field.verbose_name, field.value_to_string(self))
    

    class Meta:
        verbose_name_plural = "Appareils"
        verbose_name="Appareil"
        #managed = False  # Set to False to prevent Django from managing this table
        db_table = 'appareil_view'  # Specify the name of your existing table


class MessagesAscenseursDetails(models.Model):
    N_des_messages = models.IntegerField(primary_key=True)  
    N_ID = models.IntegerField()
    Destinataire = models.CharField(max_length=255, null=True, blank=True)
    Date = models.DateTimeField(null=True, blank=True)
    Message = models.TextField(null=True, blank=True)
    Nom = models.CharField(max_length=255, null=True, blank=True)
    Téléphone = models.CharField(max_length=255, null=True, blank=True)
    Digicode = models.CharField(max_length=255, null=True, blank=True)
    Action = models.TextField(null=True, blank=True)
    Nom_de_l_appelant = models.CharField(max_length=255, null=True, blank=True)
    Société_de_l_appelant = models.CharField(max_length=255, null=True, blank=True)
    Adresse_de_l_appelant = models.CharField(max_length=255, null=True, blank=True)
    Code_postal_de_l_appelant = models.CharField(max_length=255, null=True, blank=True)
    Ville_de_l_appelant = models.CharField(max_length=255, null=True, blank=True)
    Téléphone_de_l_appelant = models.CharField(max_length=255, null=True, blank=True)
    Digicode_de_l_appelant = models.CharField(max_length=255, null=True, blank=True)
    Nature_de_l_appel = models.CharField(max_length=255, null=True, blank=True)
    Stocké = models.CharField(max_length=255, null=True, blank=True)
    Incarcération = models.CharField(max_length=255, null=True, blank=True)
    Opérateur = models.CharField(max_length=255, null=True, blank=True)
    Téléphone_2 = models.CharField(max_length=255, null=True, blank=True)
    Confirmation = models.CharField(max_length=255, null=True, blank=True)
    ConfIncar = models.DateTimeField(null=True, blank=True)
    ConfIncar2 = models.CharField(max_length=255, null=True, blank=True)
    Commentaires = models.TextField(null=True, blank=True)
    Autres1 = models.CharField(max_length=255, null=True, blank=True)
    Autres2 = models.CharField(max_length=255, null=True, blank=True)
    Etat = models.CharField(max_length=255, null=True, blank=True)
    ville = models.CharField(max_length=100, null=True, blank=True)
    entretien = models.CharField(max_length=50, null=True, blank=True)
    Adresse = models.CharField(max_length=255, null=True, blank=True)
    Code_Postal = models.CharField(max_length=10, null=True, blank=True)
    code_client = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'MessagesAscenseursDetails'
        verbose_name = 'Message Ascenseur Detail'
        verbose_name_plural = 'Messages Ascenseurs Details'
    def get_fields(self):
         return [field.name for field in self._meta.get_fields()]
    
    def __iter__(self):
        for field in self._meta.fields:
            yield (field.verbose_name, field.value_to_string(self))

class ArchiveMessagesAscenseurs(models.Model):
    
    N_des_messages = models.AutoField(primary_key=True, verbose_name='N°des messages')
    N_ID = models.IntegerField(null=True, blank=True, verbose_name='N° ID')
    Destinataire = models.CharField(max_length=255, null=True, blank=True)
    Date = models.DateTimeField(null=True, blank=True)
    Message = models.TextField(null=True, blank=True)
    Nom = models.CharField(max_length=255, null=True, blank=True)
    Téléphone = models.CharField(max_length=255, null=True, blank=True)
    Digicode = models.CharField(max_length=255, null=True, blank=True)
    Action = models.TextField(null=True, blank=True)
    Nom_de_l_appelant = models.CharField(max_length=255, null=True, blank=True, verbose_name='Nom de l\'appelant')
    Société_de_l_appelant = models.CharField(max_length=255, null=True, blank=True, verbose_name='Société de l\'appelant')
    Adresse_de_l_appelant = models.CharField(max_length=255, null=True, blank=True, verbose_name='Adresse de l\'appelant')
    Code_postal_de_l_appelant = models.CharField(max_length=255, null=True, blank=True, verbose_name='Code postal de l\'appelant')
    Ville_de_l_appelant = models.CharField(max_length=255, null=True, blank=True, verbose_name='Ville de l\'appelant')
    Téléphone_de_l_appelant = models.CharField(max_length=255, null=True, blank=True, verbose_name='Téléphone de l\'appelant')
    Digicode_de_l_appelant = models.CharField(max_length=255, null=True, blank=True, verbose_name='Digicode de l\'appelant')
    Nature_de_l_appel = models.CharField(max_length=255, null=True, blank=True, verbose_name='Nature de l\'appel')
    Stocké = models.CharField(max_length=255, null=True, blank=True)
    Incarcération = models.CharField(max_length=255, null=True, blank=True)
    Opérateur = models.CharField(max_length=255, null=True, blank=True)
    Téléphone_2 = models.CharField(max_length=255, null=True, blank=True, verbose_name='Téléphone 2')
    Confirmation = models.CharField(max_length=255, null=True, blank=True)
    ConfIncar = models.DateTimeField(null=True, blank=True)
    ConfIncar2 = models.CharField(max_length=255, null=True, blank=True)
    Commentaires = models.TextField(null=True, blank=True)
    Autres1 = models.CharField(max_length=255, null=True, blank=True)
    Autres2 = models.CharField(max_length=255, null=True, blank=True)
    Etat = models.CharField(max_length=255, null=True, blank=True)
    ville = models.CharField(max_length=100, null=True, blank=True)
    entretien = models.CharField(max_length=50, null=True, blank=True)
    Adresse = models.CharField(max_length=255, null=True, blank=True)
    Code_Postal = models.CharField(max_length=10, null=True, blank=True)
    code_client = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'view_archive_messages_ascenseurs'
        verbose_name = 'view_archive_messages_ascenseurs'
        verbose_name_plural = 'view_archive_messages_ascenseurs'

    def get_fields(self):
         return [field.name for field in self._meta.get_fields()]
    
    def __iter__(self):
        for field in self._meta.fields:
            yield (field.verbose_name, field.value_to_string(self))

class Astreinte(models.Model):
    id_astreinte = models.AutoField(primary_key=True)
    entretien = models.CharField(max_length=50)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    priorite = models.IntegerField()
    detail_astreinte = models.CharField(max_length=200, null=True, blank=True)
    type1 = models.CharField(max_length=30, null=True, blank=True)
    media1 = models.CharField(max_length=50, null=True, blank=True)
    raccourci1 = models.CharField(max_length=15, null=True, blank=True)
    type2 = models.CharField(max_length=30, null=True, blank=True)
    media2 = models.CharField(max_length=250, null=True, blank=True)
    raccourci2 = models.CharField(max_length=15, null=True, blank=True)
    type3 = models.CharField(max_length=30, null=True, blank=True)
    media3 = models.CharField(max_length=250, null=True, blank=True)
    raccourci3 = models.CharField(max_length=15, null=True, blank=True)
    type4 = models.CharField(max_length=30, null=True, blank=True)
    media4 = models.CharField(max_length=250, null=True, blank=True)
    raccourci4 = models.CharField(max_length=15, null=True, blank=True)
    date_import = models.DateTimeField(auto_now_add=True)
    operator_create = models.CharField(max_length=50, null=True, blank=True)
    operator_update = models.CharField(max_length=50, null=True, blank=True)
    date_last_update = models.DateTimeField(null=True, blank=True)
    etat = models.CharField(max_length=30, default='libre', null=True, blank=True)
    historique_update = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'astreinte'  
        verbose_name = 'Astreinte'
        verbose_name_plural = 'Astreintes'

    def __str__(self):
        return f"{self.entretien} ({self.date_debut} - {self.date_fin})"
            