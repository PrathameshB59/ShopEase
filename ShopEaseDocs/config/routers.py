"""
Database Router for ShopEase Documentation.

Routes:
- help_center app -> 'docs' database (SQLite)
- All other apps -> 'default' database (MySQL - ShopEase)
"""


class DocsRouter:
    """
    A router to control database operations for the documentation project.

    - help_center models use the 'docs' SQLite database
    - Authentication and other Django models use the 'default' MySQL database
    """

    # Apps that should use the docs (SQLite) database
    docs_apps = {'help_center'}

    def db_for_read(self, model, **hints):
        """Route read operations."""
        if model._meta.app_label in self.docs_apps:
            return 'docs'
        return 'default'

    def db_for_write(self, model, **hints):
        """Route write operations."""
        if model._meta.app_label in self.docs_apps:
            return 'docs'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if both models are in the same database."""
        db1 = 'docs' if obj1._meta.app_label in self.docs_apps else 'default'
        db2 = 'docs' if obj2._meta.app_label in self.docs_apps else 'default'
        return db1 == db2

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Control which migrations run on which database.

        - help_center -> only on 'docs' database
        - Django built-in apps (auth, contenttypes, sessions, admin) -> never migrate
          (they already exist in ShopEase MySQL database)
        - accounts, core, code_docs -> never migrate (no models or use MySQL)
        """
        # Never migrate Django's built-in apps (they exist in ShopEase database)
        if app_label in ['auth', 'contenttypes', 'sessions', 'admin', 'accounts']:
            return False

        # help_center only migrates to docs database
        if app_label == 'help_center':
            return db == 'docs'

        # Don't migrate anything else
        return False
