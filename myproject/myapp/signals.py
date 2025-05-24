# myproject/myapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, PointActivityLog
from allauth.account.signals import user_signed_up # Import allauth signal for new signups
from django.contrib import messages # Import messages for notifications
from django.db import transaction # Import transaction for atomic operations

# Helper function to manage points (moved here for centralized logic)
def manage_points(user_instance, points_to_change, activity_type_code, description_text=""):
    try:
        profile, created = UserProfile.objects.get_or_create(user=user_instance)
        with transaction.atomic():
            # Ensure points don't go negative if deducting
            if points_to_change > 0 or (points_to_change < 0 and profile.total_points + points_to_change >= 0):
                profile.total_points = profile.total_points + points_to_change
            elif points_to_change < 0 and profile.total_points + points_to_change < 0:
                print(f"Attempted to deduct more points than available for {user_instance.username}")
                return False # Indicate failure due to insufficient points
            profile.save()

            PointActivityLog.objects.create(
                user=user_instance,
                activity_type=activity_type_code,
                points_change=points_to_change,
                description=description_text
            )
        return True
    except Exception as e:
        print(f"Error managing points for {user_instance.username}: {e}")
        return False

@receiver(post_save, sender=User)
def create_user_profile_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance) # Ensures UserProfile exists for new User

@receiver(user_signed_up)
def allauth_user_signed_up_points(request, user, **kwargs):
    """
    Awards points when a user signs up, either via regular signup form or social account.
    This signal runs after allauth completes user creation/signup.
    """
    # Check if points for 'user_signup' were already awarded to prevent duplicates
    if not PointActivityLog.objects.filter(user=user, activity_type='user_signup').exists():
        if manage_points(user, 5, 'user_signup', "ยินดีต้อนรับสมาชิกใหม่จากการสมัคร/เชื่อมต่อบัญชี!"):
            # You might want to use messages.success or messages.info here if you display them
            # However, for social logins, messages might not always be displayed immediately due to redirects.
            # messages.info(request, "ยินดีต้อนรับ! คุณได้รับ 5 แต้มสำหรับการสมัครสมาชิก/เชื่อมต่อบัญชี 🥳")
            pass # Points awarded, message is optional or handled elsewhere