# accounts/signals.py

from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile = apps.get_model('accounts', 'Profile')
        Profile.objects.create(user=instance)
