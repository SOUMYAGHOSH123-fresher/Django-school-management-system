from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=User)
def create_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)        
    else:
        instance.profile.save()





