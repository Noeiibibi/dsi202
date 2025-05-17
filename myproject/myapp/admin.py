from django.contrib import admin
from .models import (
    Category, Event, Attendance, UserProfile, Community,
    PointActivityLog, Reward, UserReward,
    EasterEgg, UserFoundEasterEgg,
    GreetingCardTemplate, UserGreetingCard
)

@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description') # เพิ่ม description เพื่อให้เห็นข้อมูลมากขึ้น
    search_fields = ('name',)
    list_filter = ('name',) # อาจจะเพิ่ม filter ถ้ามี community เยอะ

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'location', 'category', 'community', 'organizer', 'attendee_count', 'created_at') # เพิ่ม created_at
    list_filter = ('date', 'category', 'community', 'created_at', 'organizer') # เพิ่ม organizer
    search_fields = ('title', 'description', 'location', 'organizer__username', 'category__name', 'community__name') # เพิ่มการ search จาก category และ community
    date_hierarchy = 'date'
    raw_id_fields = ('organizer', 'category', 'community')
    list_per_page = 20 # แสดงผลต่อหน้า

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'event__title') # เพิ่ม filter จากชื่อ event
    search_fields = ('user__username', 'event__title')
    raw_id_fields = ('user', 'event')
    list_per_page = 20

# UserProfileAdmin (ลบอันที่ซ้ำซ้อนออก ให้เหลืออันเดียวที่สมบูรณ์)
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_points', 'profile_image', 'active_profile_frame', 'bio_short') # เพิ่ม active_profile_frame
    search_fields = ('user__username', 'bio')
    readonly_fields = ('total_points',)
    raw_id_fields = ('user', 'active_profile_frame') # ทำให้ active_profile_frame เป็น searchable dropdown
    list_select_related = ('user', 'active_profile_frame') # ช่วยลด query
    list_per_page = 20

    def bio_short(self, obj): # แสดง bio แบบย่อ
        if obj.bio:
            return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio
        return "-"
    bio_short.short_description = 'Bio (ย่อ)'

@admin.register(PointActivityLog)
class PointActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'points_change', 'timestamp', 'description')
    list_filter = ('activity_type', 'timestamp', 'user') # เพิ่ม filter จาก user
    search_fields = ('user__username', 'description', 'activity_type') # เพิ่ม activity_type
    date_hierarchy = 'timestamp'
    readonly_fields = ('user', 'activity_type', 'points_change', 'timestamp', 'description')
    list_per_page = 20

    def has_add_permission(self, request):
        return False # ป้องกันการเพิ่ม log โดยตรงจาก admin

    def has_change_permission(self, request, obj=None):
        return False # ป้องกันการแก้ไข log โดยตรงจาก admin

    # def has_delete_permission(self, request, obj=None): # อาจจะเปิดให้ลบได้ถ้าจำเป็น
    #     return False

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('name', 'reward_type', 'points_required', 'is_active', 'image_preview', 'actual_frame_image_preview')
    list_filter = ('reward_type', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'points_required') # ทำให้แก้ไข field เหล่านี้จาก list view ได้เลย
    list_per_page = 20

    def image_preview(self, obj): # แสดงรูป preview ของรางวัล
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.image.url)
        return "ไม่มีรูป"
    image_preview.short_description = 'รูป Preview'

    def actual_frame_image_preview(self, obj): # แสดงรูป preview ของกรอบจริง
        from django.utils.html import format_html
        if obj.actual_frame_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:contain; background:lightgray;" />', obj.actual_frame_image.url)
        return "ไม่มีรูปกรอบ"
    actual_frame_image_preview.short_description = 'รูปกรอบจริง'


@admin.register(UserReward)
class UserRewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward_name', 'redeemed_at')
    list_filter = ('redeemed_at', 'reward__name', 'user__username')
    search_fields = ('user__username', 'reward__name')
    readonly_fields = ('user', 'reward', 'redeemed_at')
    raw_id_fields = ('user', 'reward')
    list_select_related = ('user', 'reward')
    list_per_page = 20

    def reward_name(self, obj):
        return obj.reward.name
    reward_name.short_description = 'ชื่อของรางวัล'
    reward_name.admin_order_field = 'reward__name'


    def has_add_permission(self, request):
        return False # ป้องกันการเพิ่มโดยตรงจาก admin

@admin.register(EasterEgg)
class EasterEggAdmin(admin.ModelAdmin):
    list_display = ('name', 'unique_code', 'points_reward', 'description_short')
    search_fields = ('name', 'description', 'unique_code')
    list_editable = ('points_reward',)

    def description_short(self, obj):
        if obj.description:
            return obj.description[:70] + '...' if len(obj.description) > 70 else obj.description
        return "-"
    description_short.short_description = 'คำใบ้ (ย่อ)'

@admin.register(UserFoundEasterEgg)
class UserFoundEasterEggAdmin(admin.ModelAdmin):
    list_display = ('user', 'easter_egg_name', 'found_at')
    search_fields = ('user__username', 'easter_egg__name')
    readonly_fields = ('user', 'easter_egg', 'found_at')
    raw_id_fields = ('user', 'easter_egg')
    list_select_related = ('user', 'easter_egg')

    def easter_egg_name(self, obj):
        return obj.easter_egg.name
    easter_egg_name.short_description = 'Easter Egg'
    easter_egg_name.admin_order_field = 'easter_egg__name'

    def has_add_permission(self, request):
        return False

@admin.register(GreetingCardTemplate)
class GreetingCardTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview')
    search_fields = ('name',)

    def image_preview(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" width="100" style="object-fit:contain;" />', obj.image.url)
        return "ไม่มีรูป"
    image_preview.short_description = 'รูป Template'

@admin.register(UserGreetingCard)
class UserGreetingCardAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'card_template_name', 'sent_at', 'is_read', 'mood_icon', 'message_short')
    list_filter = ('sent_at', 'is_read', 'card_template__name', 'sender__username', 'recipient__username')
    search_fields = ('sender__username', 'recipient__username', 'custom_message')
    readonly_fields = ('sender', 'recipient', 'card_template', 'custom_message', 'mood_icon', 'sent_at', 'is_read') # ทำให้ is_read แก้ไขไม่ได้โดยตรง
    raw_id_fields = ('sender', 'recipient', 'card_template')
    list_select_related = ('sender', 'recipient', 'card_template')
    list_editable = () # ถ้าต้องการให้ is_read แก้ไขได้ ให้เอาออกจาก readonly_fields แล้วใส่ที่นี่

    def card_template_name(self, obj):
        return obj.card_template.name if obj.card_template else "-"
    card_template_name.short_description = 'Template การ์ด'
    card_template_name.admin_order_field = 'card_template__name'

    def message_short(self, obj):
        return obj.custom_message[:50] + '...' if len(obj.custom_message) > 50 else obj.custom_message
    message_short.short_description = 'ข้อความ (ย่อ)'

    def has_add_permission(self, request):
        return False