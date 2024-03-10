from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q, Max, OuterRef, Subquery, Count

User = get_user_model()
default_value = timezone.now()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='media/img/profile_pics', default='default.jpg')

    def __str__(self):
        return f'{self.user.username} Profile'

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')

    def __str__(self):
        return f'{self.follower} follows {self.followed}'

    class Meta:
        unique_together = ('follower', 'followed')
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'

class ConversationManager(models.Manager):
    def get_or_create_conversation(self, user1, user2):
        conversation = self.get_queryset().filter(members__in=[user1, user2]).annotate(num_members=Count('members')).filter(num_members=2).first()
        if conversation:
            return conversation, False
        else:
            conversation = self.model()
            conversation.save()
            conversation.members.add(user1, user2)
            return conversation, True

class Conversation(models.Model):
    subject = models.CharField(max_length=100, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(User, related_name='conversations')
    
    objects = ConversationManager()

    def __str__(self):
        return f"Conversation {self.id}: {' & '.join(member.username for member in self.members.all())}"

    def get_last_message(self):
        return self.messages.order_by('-timestamp').first()

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

