from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class LastNameAuthBackend(ModelBackend):
    """
    Authentification en utilisant last_name au lieu de username
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Rechercher l'utilisateur par last_name
            user = User.objects.get(last_name=username)
            if user.check_password(password):
                # Ne pas bloquer ici, laisser la vue gérer le cas de l'email manquant
                return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Si plusieurs utilisateurs ont le même last_name
            return None
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
