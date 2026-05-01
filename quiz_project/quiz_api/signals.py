from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=User)
def create_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

        # if getattr(instance, '_skip_welcome_email', False):
        #     return


        # # If already approved → send different email
        # if instance.is_approved:
        #     send_mail(
        #         subject="Account Approved",
        #         message="Your account has been created and approved. You can now login and start using the system.",
        #         from_email=settings.EMAIL_HOST_USER,
        #         recipient_list=[instance.email],
        #         fail_silently=False,
        #     )
        # else:
        #     # Default flow (normal registration)
        #     send_mail(
        #         subject="Registration Successful",
        #         message="Thank you for registering. Please wait until the principal approves your account.",
        #         from_email=settings.EMAIL_HOST_USER,
        #         recipient_list=[instance.email],
        #         fail_silently=False,
        #     )
        
    else:
        instance.profile.save()





