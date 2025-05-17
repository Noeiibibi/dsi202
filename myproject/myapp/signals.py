# myproject/myapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, PointActivityLog
# from .views import manage_points # ไม่ควร import จาก views โดยตรง

# ย้าย manage_points ไป myapp/utils.py แล้ว import จากที่นั่น
# หรือทำ helper function เล็กๆ ในนี้
# from .utils import award_points_for_activity (ชื่อสมมติ)

@receiver(post_save, sender=User)
def create_user_profile_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        # ถ้าจะให้แต้มตอนสมัครผ่าน signal ก็ทำตรงนี้
        # success = manage_points(instance, 5, 'user_signup', "Welcome! You earned points for signing up.")
        # if success:
        #     print(f"Awarded signup points to {instance.username}")

# @receiver(post_save, sender=UserProfile)
# def award_profile_completion_points_signal(sender, instance, created, **kwargs):
#     # Logic การให้แต้มเมื่อ profile complete อาจจะซับซ้อน
#     # และอาจจะเหมาะกับการทำใน view หลังจาก user submit form edit_profile มากกว่า
#     # เพื่อให้แน่ใจว่า user ตั้งใจกรอกข้อมูลจริงๆ
#     # เช่น
#     # user = instance.user
#     # if instance.bio and instance.profile_image and instance.profile_image.name != UserProfile._meta.get_field('profile_image').get_default():
#     #     # Check if points for 'profile_complete_basic' or 'profile_complete_picture' already awarded
#     #     if not PointActivityLog.objects.filter(user=user, activity_type='profile_complete_basic').exists():
#     #         manage_points(user, 10, 'profile_complete_basic', "Bio information added.")
#     #     if not PointActivityLog.objects.filter(user=user, activity_type='profile_complete_picture').exists():
#     #         manage_points(user, 15, 'profile_complete_picture', "Profile picture uploaded.")
#     pass