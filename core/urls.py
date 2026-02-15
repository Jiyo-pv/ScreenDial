from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('session/create/', views.create_session, name='create_session'),
    path('session/join/', views.join_session, name='join_session'),
    path('session/<str:room_code>/', views.session_room, name='session_room'),
    path('session/<str:room_code>/control/', views.session_control, name='session_control'),
    path('session/<str:room_code>/add/', views.add_participant, name='add_participant'),
    path('session/<str:room_code>/delete/', views.delete_session, name='delete_session'),
    path('session/<str:room_code>/waiting/', views.waiting_room, name='waiting_room'),
    path('session/<str:room_code>/check-status/', views.check_status, name='check_status'),
    path('session/<str:room_code>/toggle-discovery/', views.toggle_discoverability, name='toggle_discoverability'),
    path('profile/', views.profile_view, name='profile'),

    # Invitation flow
    path('api/invite/', views.invite_participant, name='invite_participant'),
    path('api/my-invitations/', views.my_invitations, name='my_invitations'),
    path('api/available-sessions/', views.available_sessions, name='available_sessions'),
    path('api/respond-invite/', views.respond_invite, name='respond_invite'),

    # Room code join flow
    path('api/join-with-code/', views.join_with_code, name='join_with_code'),

    # Host control panel
    path('api/session-requests/<str:room_code>/', views.session_requests, name='session_requests'),
    path('api/handle-request/', views.handle_request, name='handle_request'),
]
