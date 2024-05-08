class PrimaryRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label=='gisapp':
            print ("will use GIS db")
            return "gisapp"
        else:
            return "data_db"

    def db_for_write(self, model, **hints):
        if model._meta.app_label=='gisapp':
            print ("will use GIS db")
            return "gisapp"
        else:
            return "data_db"

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed if both objects are
        in the primary/replica pool.
        """
        db_set = {"data_db", "gisapp"}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        All non-auth models end up in this pool.
        """
        return True

