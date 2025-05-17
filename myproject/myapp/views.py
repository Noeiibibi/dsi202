# myproject/myapp/views.py

# Django Core Imports
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages # <--- ตรวจสอบว่า import messages แล้ว
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.http import HttpResponseForbidden, HttpResponse
from django.db.models import Q

# Django REST framework Imports
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

# Local Imports (จาก app ของคุณ)
from .models import (
    Event, Category, Attendance, UserProfile, Community,
    PointActivityLog, Reward, UserReward,
    EasterEgg, UserFoundEasterEgg,
    GreetingCardTemplate, UserGreetingCard
)
from .forms import EventForm, UserProfileForm
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    CommunitySerializer,
    CategorySerializer,
    EventSerializer,
    EventDetailSerializer,
    AttendanceSerializer
)

# --- Helper function manage_points ---
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

# --- Views เดิมของคุณ ---
def index(request):
    return redirect('home')

def home(request):
    communities = Community.objects.all().order_by('-id')[:4]
    categories = Category.objects.all()[:5]
    today = timezone.now().date()
    featured_events = Event.objects.filter(date__gte=today).order_by('date')[:4]

    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        today_min = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_max = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        has_daily_login_today = PointActivityLog.objects.filter(
            user=request.user, activity_type='daily_login', timestamp__range=(today_min, today_max)
        ).exists()
        if not has_daily_login_today:
            if manage_points(request.user, 5, 'daily_login', "เข้าสู่ระบบรายวัน"):
                # messages.info(request, "คุณได้รับ 5 แต้มสำหรับการเข้าสู่ระบบวันนี้! ☀️") # Optional message
                pass
    context = {
        'communities': communities if communities.exists() else [],
        'categories': categories if categories.exists() else [],
        'featured_events': featured_events if featured_events.exists() else [],
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
        if category_id: queryset = queryset.filter(category_id=category_id)
        community_id = self.request.GET.get('community')
        if community_id: queryset = queryset.filter(community_id=community_id)
        search_query = self.request.GET.get('search')
        if search_query: queryset = queryset.filter( Q(title__icontains=search_query) | Q(description__icontains=search_query) | Q(location__icontains=search_query))
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['communities'] = Community.objects.all()
        context['selected_category'] = self.request.GET.get('category')
        context['selected_community'] = self.request.GET.get('community')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class EventDetailView(DetailView):
    model = Event
    template_name = 'myapp/event_detail.html'
    context_object_name = 'event'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try: context['attendance'] = Attendance.objects.get(event=self.object, user=self.request.user)
            except Attendance.DoesNotExist: context['attendance'] = None
        context['attendees'] = self.object.attendees.filter(status='attending')
        context['interested'] = self.object.attendees.filter(status='interested')
        if self.object.category: context['related_events'] = Event.objects.filter(category=self.object.category).exclude(id=self.object.id).order_by('?')[:4]
        else: context['related_events'] = Event.objects.none()
        return context

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'myapp/event_form.html'

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        try:
            self.object = form.save() # Save event first
            # Award points for creating an event
            if manage_points(self.request.user, 25, 'create_event', f"สร้างกิจกรรม: {self.object.title}"):
                 messages.success(self.request, f"กิจกรรม '{self.object.title}' ถูกสร้างเรียบร้อย และคุณได้รับ 25 แต้ม! 🎉")
            else:
                messages.warning(self.request, f"กิจกรรม '{self.object.title}' ถูกสร้างเรียบร้อย แต่เกิดข้อผิดพลาดในการบันทึกแต้ม")
            return redirect(reverse_lazy('event_detail', kwargs={'pk': self.object.pk}))
        except Exception as e:
            messages.error(self.request, f"เกิดข้อผิดพลาดในการสร้างกิจกรรม: {e}")
            return self.form_invalid(form)

class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'myapp/event_form.html'
    def get_success_url(self): return reverse_lazy('event_detail', kwargs={'pk': self.object.pk})
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.organizer != self.request.user and not request.user.is_superuser:
            messages.error(request, "คุณไม่มีสิทธิ์แก้ไขกิจกรรมนี้ค่ะ")
            return redirect('event_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

@login_required
def attend_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    status = request.POST.get('status', 'attending')
    attendance, created = Attendance.objects.update_or_create(event=event, user=request.user, defaults={'status': status})

    if status == 'attending':
        log_description = f"เข้าร่วมกิจกรรม: {event.title}"
        # Check if points for this specific event joining action were already awarded
        already_got_points_for_this_event_action = PointActivityLog.objects.filter(
            user=request.user,
            activity_type='join_event',
            description=log_description # For simplicity. A more robust way is to link PointActivityLog to Event model.
        ).exists()

        if not already_got_points_for_this_event_action:
            if manage_points(request.user, 10, 'join_event', log_description):
                messages.info(request, f"คุณได้รับ 10 แต้มสำหรับการเข้าร่วมกิจกรรม '{event.title}'! 👍")
        
        if created : # If a new attendance record was created (first time setting status for this event)
             messages.success(request, f"คุณได้ยืนยันเข้าร่วมกิจกรรม '{event.title}' เรียบร้อยแล้วค่ะ")
        else: # If an existing attendance record was updated
            messages.success(request, f"สถานะการเข้าร่วมกิจกรรม '{event.title}' ของคุณถูกอัปเดตแล้วค่ะ")

    elif status == 'interested':
        messages.success(request, f"คุณได้แสดงความสนใจกิจกรรม '{event.title}' แล้วค่ะ")
    return redirect('event_detail', pk=pk)

@login_required
def user_profile(request, username=None):
    target_user = get_object_or_404(User, username=username) if username else request.user
    profile, created = UserProfile.objects.get_or_create(user=target_user) # Ensures profile exists
    organized_events = Event.objects.filter(organizer=target_user).order_by('-date', '-time')
    attending_events_ids = Attendance.objects.filter(user=target_user, status='attending').values_list('event_id', flat=True)
    attending_events = Event.objects.filter(id__in=attending_events_ids).order_by('-date', '-time')
    context = {'profile_user': target_user, 'profile': profile, 'organized_events': organized_events, 'attending_events': attending_events}
    return render(request, 'myapp/user_profile.html', context)


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    # ดึงรายการกรอบโปรไฟล์ทั้งหมดที่ผู้ใช้คนนี้แลกมาแล้ว (เป็น Reward objects)
    owned_frames = Reward.objects.filter(
        reward_type='profile_frame',
        userreward__user=request.user # ตรวจสอบผ่านตาราง UserReward
    ).distinct() # ใช้ distinct เผื่อกรณีมีการแลกซ้ำ (แต่ model UserReward ควรมี unique_together ป้องกันอยู่แล้ว)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            saved_profile = form.save(commit=False)

            selected_frame_id = request.POST.get('active_frame_selector')
            if selected_frame_id:
                try:
                    # ตรวจสอบว่า frame ที่เลือกมานั้น user เป็นเจ้าของจริงๆ และเป็นประเภท profile_frame
                    chosen_frame = owned_frames.get(id=selected_frame_id)
                    saved_profile.active_profile_frame = chosen_frame
                except Reward.DoesNotExist:
                    messages.warning(request, "กรอบโปรไฟล์ที่เลือกไม่ถูกต้อง")
                    # ไม่เปลี่ยนค่า active_profile_frame เดิม ถ้าเลือกผิด
            else:
                saved_profile.active_profile_frame = None # ถ้าผู้ใช้เลือก "ไม่มีกรอบ"

            saved_profile.save()
            # ... (โค้ดการให้แต้มสำหรับการแก้ไขโปรไฟล์ของคุณ) ...
            messages.success(request, "โปรไฟล์ของคุณถูกบันทึกเรียบร้อยแล้วค่ะ")
            return redirect('user_profile')
        else:
            messages.error(request, "เกิดข้อผิดพลาดในการบันทึกโปรไฟล์ กรุณาตรวจสอบข้อมูลอีกครั้ง")
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'owned_profile_frames': owned_frames, # ส่งไปให้ template เพื่อสร้าง dropdown
        'current_active_frame_id': profile.active_profile_frame.id if profile.active_profile_frame else None, # ส่ง ID ของ frame ที่ active อยู่
    }
    return render(request, 'myapp/edit_profile.html', context)


@login_required
def user_profile(request, username=None):
    target_user = get_object_or_404(User, username=username) if username else request.user
    profile, created = UserProfile.objects.get_or_create(user=target_user)
    organized_events = Event.objects.filter(organizer=target_user).order_by('-date', '-time')
    attending_events_ids = Attendance.objects.filter(user=target_user, status='attending').values_list('event_id', flat=True)
    attending_events = Event.objects.filter(id__in=attending_events_ids).order_by('-date', '-time')
    
    # ตรวจสอบว่า profile.active_profile_frame มี object หรือไม่ก่อนจะพยายามเข้าถึง attribute
    active_frame_url = None
    active_frame_name = None
    if profile.active_profile_frame:
        # **สำคัญมาก:** แก้ไข .actual_frame_image ให้ตรงกับชื่อ field ที่คุณใช้เก็บรูปกรอบจริงใน Reward model
        if hasattr(profile.active_profile_frame, 'actual_frame_image') and profile.active_profile_frame.actual_frame_image:
            active_frame_url = profile.active_profile_frame.actual_frame_image.url
        elif profile.active_profile_frame.image: # Fallback ไปใช้ image ถ้า actual_frame_image ไม่มี
             active_frame_url = profile.active_profile_frame.image.url
        active_frame_name = profile.active_profile_frame.name


    context = {
        'profile_user': target_user,
        'profile': profile, # profile object ทั้งหมดจะถูกส่งไป ซึ่งรวม active_profile_frame อยู่แล้ว
        'organized_events': organized_events,
        'attending_events': attending_events,
        'active_profile_frame_url': active_frame_url, # ส่ง URL ไปโดยตรงเพื่อความสะดวก
        'active_profile_frame_name': active_frame_name, # ส่งชื่อไปด้วย (ถ้าต้องการ)
    }
    return render(request, 'myapp/user_profile.html', context)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user) 
            login(request, user)
            # Award points for new signup
            if manage_points(user, 5, 'user_signup', "ยินดีต้อนรับสมาชิกใหม่!"):
               messages.info(request, "ยินดีต้อนรับ! คุณได้รับ 5 แต้มสำหรับการสมัครสมาชิก 🥳")
            return redirect('home')
    else: form = UserCreationForm()
    return render(request, 'myapp/signup.html', {'form': form})

# --- Views ใหม่สำหรับระบบแต้มและของรางวัล ---
@login_required
def rewards_store_view(request):
    rewards_queryset = Reward.objects.filter(is_active=True).order_by('points_required')
    profile = get_object_or_404(UserProfile, user=request.user)
    # ดึง list ของ ID ของ badge ที่ user มีอยู่แล้ว
    user_owned_badge_ids = list(UserReward.objects.filter(
        user=request.user,
        reward__reward_type='badge'
    ).values_list('reward_id', flat=True))

    # เตรียม list ของ rewards พร้อมสถานะ 'is_owned_badge'
    rewards_data_for_template = []
    for reward_item in rewards_queryset:
        # คำนวณ is_owned_badge สำหรับแต่ละ reward
        # is_owned_badge จะเป็น true ถ้า reward_type คือ 'badge' และ reward_item.id อยู่ใน list ที่ผู้ใช้มี
        is_owned_badge_for_this_reward = (
            reward_item.reward_type == 'badge' and
            reward_item.id in user_owned_badge_ids
        )
        rewards_data_for_template.append({
            'reward': reward_item, # ตัว object ของ Reward
            'is_owned_badge': is_owned_badge_for_this_reward # ค่า boolean ที่คำนวณแล้ว
        })

    context = {
        'rewards_data': rewards_data_for_template, # ส่ง list ใหม่นี้ไปให้ template
        'user_profile': profile,
        'page_title': "ร้านค้าของรางวัลสุดพิเศษ"
    }
    return render(request, 'myapp/rewards_store.html', context)

@login_required
@transaction.atomic
def redeem_reward_view(request, reward_id):
    if request.method != 'POST': return HttpResponseForbidden("อนุญาตเฉพาะ POST method ค่ะ")
    reward = get_object_or_404(Reward, id=reward_id, is_active=True)
    profile = get_object_or_404(UserProfile, user=request.user)
    if reward.reward_type == 'badge' and UserReward.objects.filter(user=request.user, reward=reward).exists():
        messages.warning(request, f"คุณเคยแลก '{reward.name}' ไปแล้วค่ะ")
        return redirect('rewards_store')
    if profile.total_points >= reward.points_required:
        if manage_points(request.user, -reward.points_required, 'redeem_reward', f"แลกของรางวัล: {reward.name}"):
            try:
                UserReward.objects.create(user=request.user, reward=reward)
                messages.success(request, f"ยินดีด้วย! คุณแลก '{reward.name}' สำเร็จแล้วค่ะ 🎁")
            except IntegrityError: messages.error(request, "ดูเหมือนว่าคุณเพิ่งจะแลกของรางวัลนี้ไปนะคะ")
            except Exception as e:
                messages.error(request, f"เกิดข้อผิดพลาดในการบันทึกการแลกของรางวัล: {e}")
                manage_points(request.user, reward.points_required, 'redeem_reward_failed_reversal', f"คืนแต้มจากการแลก '{reward.name}' ล้มเหลว")
        else: messages.error(request, "เกิดข้อผิดพลาดในการหักแต้มสะสมของคุณ")
    else: messages.error(request, "อุ๊ปส์! แต้มของคุณไม่พอสำหรับแลกของรางวัลนี้ค่ะ 😥")
    return redirect('rewards_store')

@login_required
def points_history_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    point_logs = PointActivityLog.objects.filter(user=request.user).order_by('-timestamp')
    rewards_owned = UserReward.objects.filter(user=request.user).select_related('reward').order_by('-redeemed_at')
    context = {'profile': profile, 'point_logs': point_logs, 'rewards_owned': rewards_owned, 'page_title': "ประวัติแต้มและของรางวัล"}
    return render(request, 'myapp/points_history.html', context)

# --- DRF ViewSets ---
# (โค้ด ViewSets ของคุณควรจะอยู่ที่นี่ และมี import ที่ถูกต้องตามที่แก้ไขไปแล้ว)
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
        if self.request.user.is_superuser: return UserProfile.objects.all()
        if self.request.user.is_authenticated: return UserProfile.objects.filter(user=self.request.user)
        return UserProfile.objects.none()
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
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
        serializer = EventSerializer(events, many=True, context={'request': request})
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
        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().select_related('organizer', 'category', 'community')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location', 'category__name', 'community__name', 'organizer__username']
    ordering_fields = ['date', 'time', 'created_at']
    def get_serializer_class(self): return EventDetailSerializer if self.action == 'retrieve' else EventSerializer
    def get_serializer_context(self): return {'request': self.request}
    def perform_create(self, serializer): serializer.save(organizer=self.request.user)
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def attend(self, request, pk=None):
        event = self.get_object()
        status = request.data.get('status', 'attending')
        attendance, created = Attendance.objects.update_or_create(event=event, user=request.user, defaults={'status': status})
        serializer = AttendanceSerializer(attendance, context={'request': request})
        return Response(serializer.data)
    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def cancel_attendance(self, request, pk=None):
        event = self.get_object()
        attendance = get_object_or_404(Attendance, event=event, user=request.user)
        attendance.delete(); return Response({"status": "canceled"})

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        queryset = Attendance.objects.filter(user=self.request.user)
        event_id = self.request.query_params.get('event')
        if event_id: queryset = queryset.filter(event_id=event_id)
        return queryset
    def perform_create(self, serializer): serializer.save(user=self.request.user)

def dashboard_page(request):
    if not request.user.is_superuser: return HttpResponseForbidden("คุณไม่มีสิทธิ์เข้าถึงหน้านี้ค่ะ")
    user_count = User.objects.count(); event_count = Event.objects.count(); community_count = Community.objects.count(); attendance_count = Attendance.objects.count()
    context = {'user_count': user_count, 'event_count': event_count, 'community_count': community_count, 'attendance_count': attendance_count}
    return render(request, 'myapp/dashboard.html', context)

