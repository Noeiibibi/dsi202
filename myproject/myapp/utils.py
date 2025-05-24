# myproject/myapp/utils.py

from django.db import transaction
from .models import UserProfile, PointActivityLog # ต้อง import models ที่เกี่ยวข้องด้วย
from django.utils import timezone 

def manage_points(user_instance, points_to_change, activity_type_code, description_text=""):
    try:
        profile, created = UserProfile.objects.get_or_create(user=user_instance)
        with transaction.atomic():
            if points_to_change > 0 or (points_to_change < 0 and profile.total_points + points_to_change >= 0):
                profile.total_points = profile.total_points + points_to_change
            elif points_to_change < 0 and profile.total_points + points_to_change < 0:
                print(f"Attempted to deduct more points than available for {user_instance.username}")
                return False
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