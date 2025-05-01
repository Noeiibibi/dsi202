
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Community, Category, Event, Attendance, UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'profile_image']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']

class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ['id', 'name', 'image', 'description']

class AttendanceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['id', 'event', 'user', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        # ใช้ user จาก request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class EventSerializer(serializers.ModelSerializer):
    attendee_count = serializers.IntegerField(read_only=True)
    organizer = UserSerializer(read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'location', 'date', 
            'time', 'image', 'category', 'community', 'organizer',
            'max_attendees', 'attendee_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'organizer']
    
    def create(self, validated_data):
        # ใช้ user ปัจจุบันเป็น organizer
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)

class EventDetailSerializer(EventSerializer):
    category = CategorySerializer(read_only=True)
    community = CommunitySerializer(read_only=True)
    attendees = serializers.SerializerMethodField()
    
    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['attendees']
    
    def get_attendees(self, obj):
        attendances = obj.attendees.all()
        return AttendanceSerializer(attendances, many=True).data