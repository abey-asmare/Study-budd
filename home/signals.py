from django.db.models.signals import post_save  # signal
from django.contrib.auth.models import User  # sender
from .models import UserProfile
from django.dispatch import receiver  # reciever


@receiver(signal=post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


