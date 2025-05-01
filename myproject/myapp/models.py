from django.db import models
from django.contrib.auth.models import User

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
    image = models.ImageField(upload_to='events/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    max_attendees = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def attendee_count(self):
        return self.attendees.count()

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

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    def __str__(self):
        return self.user.username
    
from django.db import models

