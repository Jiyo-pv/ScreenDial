from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from requests import request, session
from .models import Session, Participant, Notification


def index(request):

    hosted_sessions = []
    joined_sessions = []

    if request.user.is_authenticated:

        hosted_sessions = Session.objects.filter(
            host=request.user,
            is_active=True
        ).order_by('-created_at')

        joined_sessions = Session.objects.filter(
            participants__user=request.user,
            participants__status='accepted',
            is_active=True
        ).exclude(
            host=request.user  # avoid duplicates
        ).distinct().order_by('-created_at')

    return render(request, 'core/index.html', {
        'hosted_sessions': hosted_sessions,
        'joined_sessions': joined_sessions,
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})


@login_required
def create_session(request):
    if request.method == 'POST':
        max_participants = request.POST.get('max_participants', 10)
        try:
            max_participants = int(max_participants)
            if max_participants < 1:
                max_participants = 10
        except (ValueError, TypeError):
            max_participants = 10

        suggestions_enabled = request.POST.get('suggestions_enabled') == 'on'

        session = Session.objects.create(
            host=request.user,
            max_participants=max_participants,
            is_suggestions_enabled=suggestions_enabled,
        )
        # Add host as a participant
        Participant.objects.create(
            user=request.user,
            session=session,
            display_name=request.user.username,
            status='accepted',
            connection_quality='high'
        )
        return redirect('session_room', room_code=session.room_code)
    return redirect('index')


@login_required
def join_session(request):
    if request.method == 'POST':
        room_code = request.POST.get('room_code', '').strip()
        try:
            session = Session.objects.get(room_code=room_code, is_active=True)

            # Check participant limit
            current_count = session.participants.exclude(status__in=['rejected', 'kicked']).count()
            if current_count >= session.max_participants:
                return render(request, 'core/index.html', {
                    'error': f'Session is full ({session.max_participants} participants max).'
                })

            # Create participant entry if not exists
            participant, created = Participant.objects.get_or_create(
                user=request.user,
                session=session,
                defaults={'display_name': request.user.username, 'status': 'pending'}
            )

            # If host, ensure accepted
            if session.host == request.user:
                participant.status = 'accepted'
                participant.save()

            # If previously kicked, block re-entry
            if participant.status == 'kicked':
                return render(request, 'core/index.html', {
                    'error': 'You have been removed from this session.'
                })

            # If previously rejected, block re-entry
            if participant.status == 'rejected':
                return render(request, 'core/index.html', {
                    'error': 'Your request to join was rejected.'
                })

            return redirect('session_room', room_code=room_code)
        except Session.DoesNotExist:
            return render(request, 'core/index.html', {'error': 'Invalid Room Code'})
    return redirect('index')

@login_required
def session_room(request, room_code):

    session = get_object_or_404(Session, room_code=room_code)
    participant = get_object_or_404(Participant, user=request.user, session=session)

    # ⭐ MUST BE INSIDE FUNCTION
    pending_requests = session.participants.filter(
        status='pending',
        request_type='join_request'
    )

    invited_users = session.participants.filter(
        status='pending',
        request_type='invite'
    )

    # Redirect pending participants to waiting room
    if participant.status == 'pending':
        return redirect('waiting_room', room_code=room_code)

    if participant.status in ('rejected', 'kicked'):
        return render(request, 'core/index.html', {
            'error': 'You have been removed from this session.'
        })

    is_host = session.host == request.user

    participants_list = session.participants.exclude(user=session.host).order_by('joined_at')

    current_count = session.participants.exclude(status__in=['rejected', 'kicked']).count()

    discoverable_users = User.objects.filter(profile__is_discoverable=True).exclude(
        id__in=session.participants.filter(status__in=['accepted', 'pending']).values_list('user_id', flat=True)
    ).exclude(id=request.user.id).order_by('username')

    context = {
        'session': session,
        'participant': participant,
        'is_host': is_host,
        'room_code': room_code,
        'participants_list': participants_list,
        'current_count': current_count,
        'discoverable_users': discoverable_users,

        # ⭐ NEW
        'pending_requests': pending_requests,
        'invited_users': invited_users,
    }

    return render(request, 'core/session.html', context)

@login_required
def session_control(request, room_code):
    """Host-only endpoint to accept/reject/kick participants."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    session = get_object_or_404(Session, room_code=room_code)

    # Only host can control
    if session.host != request.user:
        return JsonResponse({'error': 'Only the host can manage participants.'}, status=403)

    action = request.POST.get('action')
    target_username = request.POST.get('username')

    if not action or not target_username:
        return JsonResponse({'error': 'Missing action or username.'}, status=400)

    if action == 'toggle_suggestions':
        session.is_suggestions_enabled = not session.is_suggestions_enabled
        session.save()
        status_str = "enabled" if session.is_suggestions_enabled else "disabled"
        return JsonResponse({
            'status': 'ok',
            'message': f'Suggestions {status_str}.',
            'is_enabled': session.is_suggestions_enabled
        })

    try:
        target_participant = Participant.objects.get(
            session=session,
            user__username=target_username
        )
    except Participant.DoesNotExist:
        return JsonResponse({'error': 'Participant not found.'}, status=404)

    # Don't allow host to kick themselves
    if target_participant.user == request.user:
        return JsonResponse({'error': 'Cannot manage yourself.'}, status=400)

    if action == 'accept':
        target_participant.status = 'accepted'
        target_participant.save()
        return JsonResponse({'status': 'ok', 'message': f'{target_username} accepted.'})

    elif action == 'reject':
        target_participant.status = 'rejected'
        target_participant.save()
        return JsonResponse({'status': 'ok', 'message': f'{target_username} rejected.'})

    elif action == 'kick':
        target_participant.status = 'kicked'
        target_participant.save()
        return JsonResponse({'status': 'ok', 'message': f'{target_username} kicked.'})

@login_required
def delete_session(request, room_code):
    session = get_object_or_404(Session, room_code=room_code, host=request.user)
    session.is_active = False
    session.save()
    return redirect('index')

@login_required
def add_participant(request, room_code):
    """Host-only endpoint to add a participant by username."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    session = get_object_or_404(Session, room_code=room_code)
    if session.host != request.user:
        return JsonResponse({'error': 'Only the host can add participants.'}, status=403)

    target_username = request.POST.get('username')
    if not target_username:
        return JsonResponse({'error': 'Missing username.'}, status=400)

    try:
        target_user = User.objects.get(username=target_username)
    except User.DoesNotExist:
        return JsonResponse({'error': f'User "{target_username}" not found.'}, status=404)

    # Check if user is already a participant
    participant = Participant.objects.filter(session=session, user=target_user).first()
    if participant:
        if participant.status in ['accepted', 'pending']:
            return JsonResponse({'error': f'{target_username} is already a participant.'}, status=400)
        
        # If they were kicked or rejected, allow re-adding them
        participant.status = 'accepted'
        participant.save()
        return JsonResponse({'status': 'ok', 'message': f'{target_username} re-added successfully.'})

    # Check participant limit
    current_count = session.participants.exclude(status__in=['rejected', 'kicked']).count()
    if current_count >= session.max_participants:
        return JsonResponse({'error': f'Session is full ({session.max_participants} max).'}, status=400)

    # Create participant (Automatically accepted since host added them)
    Participant.objects.create(
        user=target_user,
        session=session,
        display_name=target_user.username,
        status='accepted'
    )

    return JsonResponse({'status': 'ok', 'message': f'{target_username} added successfully.'})

@login_required
def profile_view(request):
    if request.method == 'POST':
        is_discoverable = request.POST.get('is_discoverable') == 'on'
        request.user.profile.is_discoverable = is_discoverable
        request.user.profile.save()
        return render(request, 'core/profile.html', {'success': 'Profile updated!'})
    return render(request, 'core/profile.html')


# ========== INVITATION FLOW ==========

@login_required
@require_http_methods(["POST"])
def invite_participant(request):
    """Host invites a participant to join session."""
    username = request.POST.get('username')
    session_id = request.POST.get('session_id')

    if not username or not session_id:
        return JsonResponse({'error': 'Missing username or session_id'}, status=400)

    session = get_object_or_404(Session, id=session_id)
    
    # Only host can invite
    if session.host != request.user:
        return JsonResponse({'error': 'Only the host can send invitations'}, status=403)

    try:
        invited_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({'error': f'User "{username}" not found'}, status=404)
    
    # Prevent inviting yourself
    if invited_user == request.user:
        return JsonResponse({'error': 'You cannot invite yourself'}, status=400)

    # Check participant limit
    current_count = session.participants.exclude(status__in=['rejected', 'disconnected']).count()
    if current_count >= session.max_participants:
        return JsonResponse({'error': f'Session is full ({session.max_participants} max)'}, status=400)

    # Create or update participant
    participant, created = Participant.objects.update_or_create(
        user=invited_user,
        session=session,
        defaults={
            'display_name': username,
            'status': 'pending',
            'request_type': 'invite'
        }
    )

    # Create notification
    Notification.objects.create(
        user=invited_user,
        message=f"You have been invited to join session {session.room_code} by {request.user.username}"
    )

    return JsonResponse({'status': 'ok', 'message': f'Invitation sent to {username}'})


@login_required
@require_http_methods(["GET"])
def my_invitations(request):
    """Get all pending invitations for the current user (only as recipient, not host)."""
    invitations = Participant.objects.filter(
        user=request.user,
        status='pending',
        request_type='invite',
        session__is_active=True
    ).exclude(
        session__host=request.user  # Exclude if user is the host
    ).select_related('session', 'session__host').values(
        'id', 'session__id', 'session__room_code', 'session__host__username', 'joined_at'
    )

    return JsonResponse({
        'status': 'ok',
        'invitations': list(invitations)
    })


@login_required
def available_sessions(request):
    """Get all available and discoverable sessions for the current user."""
    # Get sessions where user is not already a participant
    user_session_ids = Participant.objects.filter(
        user=request.user
    ).values_list('session_id', flat=True)
    
    sessions = Session.objects.filter(
        is_active=True,
        is_discoverable=True  # Only show discoverable sessions
    ).exclude(
        id__in=user_session_ids
    ).exclude(
        host=request.user
    ).select_related('host').values(
        'id', 'room_code', 'host__username', 'max_participants', 'created_at'
    ).order_by('-created_at')
    
    # Add participant counts
    sessions_list = []
    for session in sessions:
        participant_count = Participant.objects.filter(
            session_id=session['id'],
            status='accepted'
        ).count()
        session['participant_count'] = participant_count
        sessions_list.append(session)
    
    return JsonResponse({
        'status': 'ok',
        'sessions': sessions_list
    })


@login_required
@require_http_methods(["POST"])
def respond_invite(request):
    """Accept or reject an invitation."""
    session_id = request.POST.get('session_id')
    action = request.POST.get('action')  # 'accepted' or 'rejected'

    if not session_id or action not in ['accepted', 'rejected']:
        return JsonResponse({'error': 'Invalid session_id or action'}, status=400)

    participant = get_object_or_404(
        Participant,
        user=request.user,
        session__id=session_id,
        request_type='invite'
    )

    if action == 'accepted':
        participant.status = 'accepted'
        participant.save()
        return JsonResponse({'status': 'ok', 'message': 'Invitation accepted'})
    else:
        participant.status = 'rejected'
        participant.save()
        return JsonResponse({'status': 'ok', 'message': 'Invitation rejected'})


# ========== ROOM CODE JOIN FLOW ==========

@login_required
@require_http_methods(["POST"])
def join_with_code(request):
    """Participant joins with room code."""
    room_code = request.POST.get('room_code', '').strip()

    if not room_code:
        return JsonResponse({'error': 'Room code required'}, status=400)

    try:
        session = Session.objects.get(room_code=room_code, is_active=True)
    except Session.DoesNotExist:
        return JsonResponse({'error': 'Invalid or inactive room code'}, status=404)

    # Check participant limit (count only accepted participants)
    accepted_count = session.participants.filter(status='accepted').count()
    if accepted_count >= session.max_participants:
        return JsonResponse({'error': f'Session is full ({session.max_participants} max)'}, status=400)

    # Create or update participant
    participant, created = Participant.objects.update_or_create(
        user=request.user,
        session=session,
        defaults={
            'display_name': request.user.username,
            'status': 'pending',
            'request_type': 'join_request'
        }
    )

    return JsonResponse({
        'status': 'ok',
        'message': 'Join request submitted. Waiting for host approval.',
        'session_id': session.id
    })


# ========== HOST CONTROL PANEL ==========

@login_required
def session_requests(request, room_code):
    """Get all pending join requests for a session (host only)."""
    session = get_object_or_404(Session, room_code=room_code)

    # Only host can view
    if session.host != request.user:
        return JsonResponse({'error': 'Only the host can view requests'}, status=403)

    requests = Participant.objects.filter(
        session=session,
        status='pending',
        request_type='join_request'
    ).values('id', 'user__username', 'display_name', 'user__id', 'joined_at')

    return JsonResponse({
        'status': 'ok',
        'requests': list(requests)
    })


@login_required
@require_http_methods(["POST"])
def handle_request(request):
    """Host approve/reject a join request."""
    username = request.POST.get('username')
    session_id = request.POST.get('session_id')
    action = request.POST.get('action')  # 'accepted' or 'rejected'

    if not username or not session_id or action not in ['accepted', 'rejected']:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

    session = get_object_or_404(Session, id=session_id)

    # Only host can handle requests
    if session.host != request.user:
        return JsonResponse({'error': 'Only the host can handle requests'}, status=403)

    participant = get_object_or_404(
        Participant,
        session=session,
        user__username=username,
        request_type='join_request'
    )

    # Check participant limit if accepting
    if action == 'accepted':
        accepted_count = session.participants.filter(status='accepted').count()
        if accepted_count >= session.max_participants:
            return JsonResponse({'error': 'Session is now full'}, status=400)

    participant.status = action
    participant.save()

    message = f'Your join request was {action}.'
    Notification.objects.create(user=participant.user, message=message)

    return JsonResponse({'status': 'ok', 'message': f'Request {action}.'})


# ========== WAITING ROOM ==========

@login_required
def waiting_room(request, room_code):
    """View for participants waiting for host approval."""
    session = get_object_or_404(Session, room_code=room_code)
    participant = get_object_or_404(Participant, user=request.user, session=session)

    # Only pending participants see waiting room
    if participant.status != 'pending':
        return redirect('session_room', room_code=room_code)

    context = {
        'session': session,
        'participant': participant,
        'room_code': room_code
    }
    return render(request, 'core/waiting_room.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_discoverability(request, room_code):
    """Toggle whether a session is discoverable in Available Sessions (host only)."""
    session = get_object_or_404(Session, room_code=room_code)
    
    # Only host can toggle
    if session.host != request.user:
        return JsonResponse({'error': 'Only the host can change session visibility'}, status=403)
    
    # Toggle the discoverability
    session.is_discoverable = not session.is_discoverable
    session.save()
    
    status_text = "visible in Available Sessions" if session.is_discoverable else "hidden from Available Sessions"
    
    return JsonResponse({
        'status': 'ok',
        'is_discoverable': session.is_discoverable,
        'message': f'Session is now {status_text}'
    })


@login_required
def check_status(request, room_code):
    """Check participant status (for polling in waiting room)."""
    session = get_object_or_404(Session, room_code=room_code)
    participant = get_object_or_404(Participant, user=request.user, session=session)

    return JsonResponse({
        'status': participant.status,
        'message': f'Status: {participant.get_status_display()}'
    })
