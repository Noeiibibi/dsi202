# myproject/myapp/admin.py
from django.contrib import admin
from .models import (
    Category, Event, Attendance, UserProfile, Community,
    PointActivityLog, Reward, UserReward,
    EasterEgg, UserFoundEasterEgg,
    GreetingCardTemplate, UserGreetingCard
)

@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'location', 'category', 'community', 'organizer', 'attendee_count')
    list_filter = ('date', 'category', 'community', 'created_at')
    search_fields = ('title', 'description', 'location', 'organizer__username')
    date_hierarchy = 'date'
    raw_id_fields = ('organizer', 'category', 'community')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'event__title')
    raw_id_fields = ('user', 'event')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'total_points', 'profile_image')
    search_fields = ('user__username', 'bio')
    readonly_fields = ('total_points',)
    raw_id_fields = ('user',)

@admin.register(PointActivityLog)
class PointActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'points_change', 'timestamp', 'description')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__username', 'description')
    date_hierarchy = 'timestamp'
    readonly_fields = ('user', 'activity_type', 'points_change', 'timestamp', 'description')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('name', 'reward_type', 'points_required', 'is_active')
    list_filter = ('reward_type', 'is_active')
    search_fields = ('name', 'description')

@admin.register(UserReward)
class UserRewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward', 'redeemed_at')
    list_filter = ('redeemed_at', 'reward__name')
    search_fields = ('user__username', 'reward__name')
    readonly_fields = ('user', 'reward', 'redeemed_at')
    raw_id_fields = ('user', 'reward')

    def has_add_permission(self, request):
        return False

@admin.register(EasterEgg)
class EasterEggAdmin(admin.ModelAdmin):
    list_display = ('name', 'unique_code', 'points_reward')
    search_fields = ('name', 'description', 'unique_code')

@admin.register(UserFoundEasterEgg)
class UserFoundEasterEggAdmin(admin.ModelAdmin):
    list_display = ('user', 'easter_egg', 'found_at')
    search_fields = ('user__username', 'easter_egg__name')
    readonly_fields = ('user', 'easter_egg', 'found_at')
    raw_id_fields = ('user', 'easter_egg')

    def has_add_permission(self, request):
        return False

@admin.register(GreetingCardTemplate)
class GreetingCardTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')
    search_fields = ('name',)

@admin.register(UserGreetingCard)
class UserGreetingCardAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'card_template', 'sent_at', 'is_read', 'mood_icon')
    list_filter = ('sent_at', 'is_read', 'card_template')
    search_fields = ('sender__username', 'recipient__username', 'custom_message')
    readonly_fields = ('sender', 'recipient', 'card_template', 'custom_message', 'mood_icon', 'sent_at')
    raw_id_fields = ('sender', 'recipient', 'card_template')

    def has_add_permission(self, request):
        return False