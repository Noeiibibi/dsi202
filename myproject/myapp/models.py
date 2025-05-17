from django.db import models
from django.contrib.auth.models import User
# from django.utils import timezone # อาจจะได้ใช้ในอนาคตสำหรับ daily login

# Models เดิมของคุณ (Community, Category, Event, Attendance) ควรจะยังอยู่เหมือนเดิม
# ตรวจสอบให้แน่ใจว่าโค้ดด้านล่างนี้ถูกเพิ่มเข้าไป "ต่อท้าย" หรือ "รวม" กับ Model ที่มีอยู่แล้วอย่างถูกต้อง

class Community(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='communities/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Communities'


class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    image = models.ImageField(upload_to='events/', blank=True, null=True) # ทำให้สามารถเว้นว่างรูปได้
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='events') # เปลี่ยนเป็น SET_NULL
    community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True, blank=True, related_name='events') # เปลี่ยนเป็น SET_NULL
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    max_attendees = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def attendee_count(self):
        return self.attendees.filter(status='attending').count()

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('attending', 'เข้าร่วม'),
        ('interested', 'สนใจ'),
        ('not_attending', 'ไม่เข้าร่วม')
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attending_events')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='attending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f'{self.user.username} - {self.event.title} - {self.get_status_display()}'

# แก้ไข UserProfile Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True, default='profiles/fw.png') # เพิ่ม default image
    total_points = models.IntegerField(default=0) # เพิ่ม field นี้

    def __str__(self):
        return self.user.username

# --- Models ใหม่สำหรับระบบแต้มและของรางวัล ---
class PointActivityLog(models.Model):
    ACTIVITY_CHOICES = [
        ('daily_login', 'Daily Login'),
        ('profile_complete_basic', 'Profile Basic Info Added'),
        ('profile_complete_picture', 'Profile Picture Uploaded'),
        ('create_event', 'Create Event'),
        ('event_popular', 'Popular Event Created'), # แต้มถ้ากิจกรรมมีคนสนใจเยอะ
        ('join_event', 'Join Event'),
        # ('event_check_in', 'Event Check-in'), # (ขั้นสูง ถ้ามีระบบเช็คอิน)
        # ('review_event', 'Review Event'), # (ถ้ามีระบบรีวิว)
        # ('invite_friend_signup', 'Invite Friend Success'), # (ขั้นสูง ถ้ามีระบบชวนเพื่อน)
        ('found_easter_egg', 'Found Easter Egg'),
        ('sent_greeting_card', 'Sent Greeting Card'),
        # ('complete_quiz_weekly', 'Weekly Quiz Completed'), # (ถ้ามีระบบ Quiz)
        ('anniversary_signup', 'Signup Anniversary'),
        ('community_milestone', 'Community Milestone Bonus'), # Admin ให้
        ('redeem_reward', 'Redeem Reward'),
        ('redeem_reward_failed_reversal', 'Redeem Reward Failed Reversal'), # เพิ่มอันนี้
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_logs')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_CHOICES)
    points_change = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}: {self.points_change} points"

    class Meta:
        ordering = ['-timestamp']


class Reward(models.Model):
    REWARD_TYPES = [
        ('badge', 'Badge'),
        ('profile_frame', 'Profile Frame'),
        ('discount_code', 'Discount Code'),
        ('digital_good', 'Digital Good'),
        # ('chat_feature', 'Chat Feature Unlock'),
        # ('physical_item', 'Physical Item'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    points_required = models.PositiveIntegerField()
    image = models.ImageField(upload_to='rewards/', blank=True, null=True)
    reward_type = models.CharField(max_length=50, choices=REWARD_TYPES, default='badge')
    is_active = models.BooleanField(default=True)
    # data = models.JSONField(blank=True, null=True) # สำหรับเก็บข้อมูลเพิ่มเติม เช่น โค้ดส่วนลด

    def __str__(self):
        return f"{self.name} ({self.points_required} points)"

class UserReward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards_owned')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'reward')

    def __str__(self):
        return f"{self.user.username} redeemed {self.reward.name}"

# --- Models สำหรับ Easter Egg (ข้อ 6) ---
class EasterEgg(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(help_text="คำใบ้ หรือข้อความเมื่อค้นพบ")
    unique_code = models.CharField(max_length=50, unique=True, help_text="โค้ดลับสำหรับ URL หรือการตรวจสอบ")
    points_reward = models.PositiveIntegerField(default=20) # กำหนดแต้มเริ่มต้น
    # image_icon = models.ImageField(upload_to='easter_eggs/', blank=True, null=True)

    def __str__(self):
        return self.name

class UserFoundEasterEgg(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='found_easter_eggs')
    easter_egg = models.ForeignKey(EasterEgg, on_delete=models.CASCADE)
    found_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'easter_egg')

    def __str__(self):
        return f"{self.user.username} found {self.easter_egg.name}"

# --- Models สำหรับ Greeting Card (ข้อ 7) ---
class GreetingCardTemplate(models.Model):
    name = models.CharField(max_length=100) # เช่น "สุขสันต์วันเกิด ลายผีเสื้อ"
    image = models.ImageField(upload_to='greeting_cards/templates/') # รูป Template ของการ์ด
    # category = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

class UserGreetingCard(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_greetings')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_greetings')
    card_template = models.ForeignKey(GreetingCardTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    custom_message = models.TextField(max_length=500)
    mood_icon = models.CharField(max_length=10, blank=True) # เก็บ Emoji เช่น "💖", "🎉"
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Card from {self.sender.username} to {self.recipient.username} ({self.sent_at.strftime('%Y-%m-%d')})"

    class Meta:
        ordering = ['-sent_at']