from django.contrib import admin
from .models import Category, Event, Attendance, UserProfile ,Community

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
    list_filter = ('date', 'category', 'community')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'date'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'event__title')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username', 'bio')

