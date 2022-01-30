from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from chat.models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    profile_name = instance.email.split('@')[0]
    if created:
        Profile.objects.create(user=instance, name=profile_name, status='Hello There, wanna chat?')