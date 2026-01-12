"""
URL configuration for accesclient project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from . import views 
from django.contrib.auth import views as auth_views
from .views import SignUpView
from .views import export_messages_to_excel
from .views import AppareilView,ArchiveMessagesView
from .views import create_message ,modify_appareil
from .views import export_appareils_to_excel
from .views import set_appareil_perdu , modify_autres_if_meditrax ,create_astreinte,delete_astreinte,ManageTechniciansView
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='login'), name='home'),
    path('admin/', admin.site.urls),
    path('messages_ascenseurs/', views.MessagesView.as_view(), name='MessagesAscenseurs'),
    path('export-messages/', export_messages_to_excel, name='export_messages'),
    path('appareils/', AppareilView.as_view(), name='appareil_list'),
    path('export_appareils/', export_appareils_to_excel, name='export_appareils'),
    path('appareil/<int:id>/set_perdu/', set_appareil_perdu, name='set_appareil_perdu'),
    path('appareil/<int:id>/modify_autres/', modify_autres_if_meditrax, name='modify_autres_if_meditrax'),
    # Consignes
    path('consignes/', views.view_consignes, name='view_consignes'),
    # Login/logout URLs - Placed before include to override default auth views
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('archive_messages/', ArchiveMessagesView.as_view(), name='archive_messages'),
    path('export_archive_messages/', ArchiveMessagesView.as_view(), name='export_archive_messages'),

    # Password reset URLs
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    #new message page 
    path('messages/', views.messages_list, name='messages-list'),
    path('messages/<int:pk>/', views.message_detail, name='message-detail'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('create_message/<int:N_ID>/', create_message, name='create_message'),
    path('modify_appareil/<int:id>/', modify_appareil, name='modify_appareil'),
    #Astrientes
    path('create-astreinte/', create_astreinte, name='create_astreinte'),
    path('upload-excel/', views.upload_excel, name='upload_excel'),
    path('astreintes/', views.view_astreintes, name='view_astreintes'),
    path('astreinte/<int:id_astreinte>/modifier/', views.modify_astreinte, name='modify_astreinte'),
    path('astreinte/delete/<int:id_astreinte>/', views.delete_astreinte, name='delete_astreinte'),
    path('get-technician-data/<int:technician_id>/', views.get_technician_data, name='get_technician_data'),
    path('manage-technicians/', views.ManageTechniciansView.as_view(), name='manage_technicians'),
    
    # Alertes management
    path('alertes/', views.list_alertes, name='list_alertes'),
    path('api/alertes/', views.get_alertes_json, name='get_alertes_json'),
    path('api/alertes/create/', views.create_alerte, name='create_alerte'),
    path('api/alertes/<int:id_alerte>/update/', views.update_alerte, name='update_alerte'),
    path('api/alertes/<int:id_alerte>/delete/', views.delete_alerte, name='delete_alerte_api'),
    
]
