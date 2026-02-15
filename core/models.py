from django.db import models
from django.contrib.auth.models import User
import random
import string

def generate_room_code():
    return ''.join(random.choices(string.digits, k=8))

class Session(models.Model):
    room_code = models.CharField(max_length=8, unique=True, default=generate_room_code)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_sessions')
    is_active = models.BooleanField(default=True)
    is_discoverable = models.BooleanField(default=True, help_text="Allow others to see this session in Available Sessions")
    max_participants = models.IntegerField(default=10)
    is_suggestions_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.room_code} by {self.host.username}"

class Participant(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('disconnected', 'Disconnected'),
    ]
    REQUEST_TYPE_CHOICES = [
        ('invite', 'Invite'),
        ('join_request', 'Join Request'),
    ]
    CONNECTION_QUALITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='participants')
    display_name = models.CharField(max_length=50, default="Guest")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, default='join_request')
    connection_quality = models.CharField(max_length=20, choices=CONNECTION_QUALITY_CHOICES, default='high')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    # Store channel_name to send individual messages via Channels
    channel_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.display_name} in {self.session.room_code}"

class ChatMessage(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sender_name = models.CharField(max_length=50) # In case sender is Guest
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender_name}"

class AudioMessage(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='audio_messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sender_name = models.CharField(max_length=50)
    audio_file = models.FileField(upload_to='audio_messages/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Audio by {self.sender_name}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

class CommandSuggestion(models.Model):
    keyword = models.CharField(max_length=50,db_index=True, unique=True)
    suggestion = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.keyword

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_discoverable = models.BooleanField(default=True, help_text="Allow hosts to find you by username in search")

    def __str__(self):
        return f"Profile of {self.user.username}"

# Signals to auto-create profile
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    instance.profile.save()
