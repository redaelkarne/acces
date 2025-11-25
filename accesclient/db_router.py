class DatabaseRouter:
    """
    Un routeur pour contrôler toutes les opérations de base de données sur les modèles
    """

    route_app_labels = {'accesclient'}

    def db_for_read(self, model, **hints):
        """Suggère la base de données à lire."""
        if model._meta.app_label == 'accesclient':
            if model.__name__ in ['Astreinte', 'Repertoire']:
                return 'astreinte_db'
        return 'default'

    def db_for_write(self, model, **hints):
        """Suggère la base de données pour l'écriture."""
        if model._meta.app_label == 'accesclient':
            if model.__name__ in ['Astreinte', 'Repertoire']:
                return 'astreinte_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Autorise les relations si les modèles sont dans la même application."""
        db_set = {'default', 'astreinte_db'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """S'assure que certains modèles sont migrés vers la bonne base de données."""
        if app_label == 'accesclient':
            if model_name in ['astreinte', 'repertoire']:
                return db == 'astreinte_db'
            else:
                return db == 'default'
        elif db == 'astreinte_db':
            return False
        return db == 'default'
