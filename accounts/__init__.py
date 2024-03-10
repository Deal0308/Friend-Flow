# accounts/__init__.py

default_app_config = 'accounts.apps.AccountsConfig'

def ready(self):
    import accounts.signals
