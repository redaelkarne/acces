# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Appareil(models.Model):
    s_generation = models.IntegerField(db_column='s_Generation', blank=True, null=True)  # Field name made lowercase.
    s_guid = models.CharField(db_column='s_GUID', unique=True, max_length=38, blank=True, null=True)  # Field name made lowercase.
    s_lineage = models.TextField(db_column='s_Lineage', blank=True, null=True)  # Field name made lowercase.
    n_id = models.AutoField(db_column='N░ ID', unique=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    datecreation = models.DateTimeField(db_column='DateCreation', blank=True, null=True)  # Field name made lowercase.
    client = models.CharField(db_column='Client', max_length=50)  # Field name made lowercase.
    opÚrateur = models.CharField(db_column='OpÚrateur', max_length=50, blank=True, null=True)  # Field name made lowercase.
    entretien = models.CharField(db_column='Entretien', max_length=50)  # Field name made lowercase.
    destinataire = models.CharField(db_column='Destinataire', max_length=50)  # Field name made lowercase.
    tÚlÚsurveillance = models.CharField(db_column='TÚlÚsurveillance', max_length=50, blank=True, null=True)  # Field name made lowercase.
    adresse = models.CharField(db_column='Adresse', max_length=255)  # Field name made lowercase.
    code_postal = models.CharField(db_column='Code Postal', max_length=10, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    ville = models.CharField(db_column='Ville', max_length=100, blank=True, null=True)  # Field name made lowercase.
    rÚsidence = models.CharField(db_column='RÚsidence', max_length=200)  # Field name made lowercase.
    informations = models.CharField(db_column='Informations', max_length=150)  # Field name made lowercase.
    code_client = models.CharField(db_column='Code Client', max_length=50)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    type = models.CharField(db_column='Type', max_length=25, blank=True, null=True)  # Field name made lowercase.
    majfacture = models.IntegerField(db_column='MaJFacture', blank=True, null=True)  # Field name made lowercase.
    incarcÚration = models.CharField(db_column='IncarcÚration', max_length=50, blank=True, null=True)  # Field name made lowercase.
    code_consigne = models.CharField(db_column='Code consigne', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    consigne_volatile = models.CharField(db_column='Consigne volatile', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    utilisateur = models.CharField(db_column='Utilisateur', max_length=50, blank=True, null=True)  # Field name made lowercase.
    opÚrateur2 = models.CharField(db_column='OpÚrateur2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dateimport = models.DateTimeField(db_column='dateImport', blank=True, null=True)  # Field name made lowercase.
    mes = models.DateTimeField(db_column='MES', blank=True, null=True)  # Field name made lowercase.
    res = models.DateTimeField(db_column='RES', blank=True, null=True)  # Field name made lowercase.
    phonie = models.CharField(db_column='Phonie', max_length=50)  # Field name made lowercase.
    transmetteur = models.CharField(db_column='Transmetteur', max_length=200)  # Field name made lowercase.
    autres_1 = models.TextField(db_column='Autres 1', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    autres_2 = models.TextField(db_column='Autres 2', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    observations = models.CharField(db_column='Observations', max_length=2048, blank=True, null=True)  # Field name made lowercase.
    id_societe = models.IntegerField(db_column='Id_Societe', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'appareil'
