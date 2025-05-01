from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Event, Category, Attendance, UserProfile ,Community
from .forms import EventForm, UserProfileForm
from django.http import HttpResponse
from django.contrib.auth.models import User


def index(request):
    return HttpResponse("Hello from myapp!")

def home(request):
    featured_events = Event.objects.all().order_by('-created_at')[:4]
    categories = Category.objects.all()
    communities = Community.objects.all()  # เพิ่มตัวนี้เข้ามา

    context = {
        'featured_events': featured_events,
        'categories': categories,
        'communities': communities,  # ส่งไป template
    }
    return render(request, 'myapp/home.html', context)

class EventListView(ListView):
    model = Event
    template_name = 'myapp/event_list.html'
    context_object_name = 'events'
    paginate_by = 12

    def get_queryset(self):
        queryset = Event.objects.all().order_by('date', 'time')

        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        community_id = self.request.GET.get('community')
        if community_id:
            queryset = queryset.filter(community_id=community_id)

        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['communities'] = Community.objects.all()
        context['selected_category'] = self.request.GET.get('category')
        context['selected_community'] = self.request.GET.get('community')
        return context

class EventDetailView(DetailView):
    model = Event
    template_name = 'myapp/event_detail.html'
    context_object_name = 'event'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            try:
                context['attendance'] = Attendance.objects.get(
                    event=self.object,
                    user=self.request.user
                )
            except Attendance.DoesNotExist:
                context['attendance'] = None
                
        # Get list of attendees
        context['attendees'] = self.object.attendees.filter(status='attending')
        context['interested'] = self.object.attendees.filter(status='interested')
        
        # Related events (same category)
        context['related_events'] = Event.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:4]
        
        return context

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'myapp/event_form.html'
    success_url = reverse_lazy('event_list')
    
    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'myapp/event_form.html'
    
    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'pk': self.object.pk})
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.organizer != self.request.user:
            return redirect('event_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

@login_required
def attend_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    status = request.POST.get('status', 'attending')
    
    attendance, created = Attendance.objects.update_or_create(
        event=event,
        user=request.user,
        defaults={'status': status}
    )
    
    return redirect('event_detail', pk=pk)

@login_required
def user_profile(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Events organized by the user
    organized_events = Event.objects.filter(organizer=user)
    
    # Events the user is attending
    attending_events = Event.objects.filter(
        attendees__user=user,
        attendees__status='attending'
    )
    
    context = {
        'profile': profile,
        'organized_events': organized_events,
        'attending_events': attending_events,
    }
    
    return render(request, 'myapp/user_profile.html', context)

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
    }
    
    return render(request, 'myapp/edit_profile.html', context)

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            # Login the user
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'myapp/signup.html', {'form': form})

# 2. views.py - สร้าง ViewSet สำหรับแต่ละโมเดล

from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Community, Category, Event, Attendance, UserProfile
from .serializers import (
    CommunitySerializer, CategorySerializer, EventSerializer, 
    EventDetailSerializer, AttendanceSerializer, UserProfileSerializer,
    UserSerializer
)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # ถ้าเป็น superuser ให้เห็นทั้งหมด ถ้าไม่ให้เห็นแค่ของตัวเอง
        if self.request.user.is_superuser:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        community = self.get_object()
        events = Event.objects.filter(community=community)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        category = self.get_object()
        events = Event.objects.filter(category=category)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['date', 'time', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EventDetailSerializer
        return EventSerializer
    
    @action(detail=True, methods=['post'])
    def attend(self, request, pk=None):
        event = self.get_object()
        status = request.data.get('status', 'attending')
        
        # สร้างหรืออัปเดต attendance
        attendance, created = Attendance.objects.update_or_create(
            event=event,
            user=request.user,
            defaults={'status': status}
        )
        
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'])
    def cancel_attendance(self, request, pk=None):
        event = self.get_object()
        attendance = get_object_or_404(Attendance, event=event, user=request.user)
        attendance.delete()
        return Response({"status": "canceled"})

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Default: show only user's attendances
        queryset = Attendance.objects.filter(user=self.request.user)
        
        # Filter by event if provided
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
            
        return queryset
    

def dashboard_page(request):
    user_count = User.objects.count()
    event_count = Event.objects.count()
    community_count = Community.objects.count()
    attendance_count = Attendance.objects.count()

    context = {
        'user_count': user_count,
        'event_count': event_count,
        'community_count': community_count,
        'attendance_count': attendance_count,
    }
    return render(request, 'myapp/dashboard.html', context)
