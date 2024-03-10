import json
import logging
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404, render, redirect
from .forms import ProfileForm
from .models import Profile, Follow, Message, Conversation, ConversationManager, User
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic.edit import UpdateView
from django.utils import timezone
from .forms import MessageForm


User = get_user_model()
logger = logging.getLogger(__name__)

class SignUpView(CreateView):
    template_name = 'registration/signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('create_profile')

class CreateProfileView(LoginRequiredMixin, CreateView):
    template_name = 'registration/create_profile.html'
    model = Profile
    fields = ['bio', 'photo']  # Add fields from your Profile model

    def form_valid(self, form):
        form.instance.user = self.request.user  # Set the user of the profile
        return super(CreateProfileView, self).form_valid(form)

    def get_success_url(self):
    # Using the 'user_id' argument in 'reverse' function to comply with the updated 'profile' URL pattern
        return reverse('profile', kwargs={'user_id': self.request.user.id})

class HomeView(TemplateView):
    template_name = 'home.html'

class AboutView(TemplateView):
    template_name = 'about.html'

login_required
def profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    context = {'user': user}
    return render(request, 'profile.html', context)


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = 'registration/profile_edit.html'
    model = Profile
    fields = ['bio', 'photo']

    def get_object(self, queryset=None):
        # Return the profile of the currently logged-in user
        return self.request.user.profile

    def get_success_url(self):
    # Using the 'user_id' argument in 'reverse' function to comply with the updated 'profile' URL pattern
        return reverse('profile', kwargs={'user_id': self.object.user.id})


class FollowView(View):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        if user_id and action in ['follow', 'unfollow']:
            try:
                user_to_follow = User.objects.get(pk=user_id)
                user = request.user

                print("user_to_follow: ", user_to_follow.id)
                print("user: ", user.id)

                if action == 'follow':
                    Follow.objects.get_or_create(follower=user, followed=user_to_follow)
                else:
                    Follow.objects.filter(follower=user, followed=user_to_follow).delete()
                return JsonResponse({'status': 'success'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

class FollowersView(TemplateView):
    template_name = 'followers.html'

class FollowingView(TemplateView):
    template_name = 'following.html'

class ProfileView(TemplateView):
    template_name = 'profile.html'

def get_following(request):
    if request.method == 'GET':
        user = request.user
        following_users = Follow.objects.filter(follower=user).values('followed__username')
        following_list = [entry['followed__username'] for entry in following_users]
        return JsonResponse({'following': following_list})
    else:
        return JsonResponse({}, status=400)

def get_followers(request):
    if request.method == 'GET':
        user = request.user
        follower_users = Follow.objects.filter(followed=user).values('follower__username')
        follower_list = [entry['follower__username'] for entry in follower_users]
        return JsonResponse({'followers': follower_list})
    else:
        return JsonResponse({}, status=400)


class ConversationListView(ListView):
    model = Conversation
    template_name = 'home/conversation_list.html'

    def get_queryset(self):
        return Conversation.objects.filter(members=self.request.user).distinct()


@login_required
@require_POST
def reply_to_conversation(request, conversation_id):
    try:
        data = json.loads(request.body)
        form = MessageForm(data)
        
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation_id = conversation_id  # Set the conversation
            message.sender = request.user  # Set the sender to the current user
            message.save()
            return JsonResponse({'message': 'Reply successfully added.'})
        else:
            return JsonResponse({'error': 'Invalid form submission.', 'details': form.errors.as_json()}, status=400)
    except json.JSONDecodeError as e:
        return JsonResponse({'error': 'Invalid JSON data.', 'details': str(e)}, status=400)
@require_http_methods(["DELETE"])
@login_required
def delete_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, members=request.user)
    conversation.delete()
    return JsonResponse({'status': 'success', 'message': 'Conversation deleted successfully.'})
@method_decorator(login_required, name='dispatch')
class ConversationDetailView(View):
    template_name = 'conversation_detail.html'
    def get(self, request, conversation_id):
        conversation = Conversation.objects.get(id=conversation_id, members=request.user)
        return render(request, 'home/conversation_detail.html', {'conversation': conversation})

    def post(self, request, conversation_id):
        conversation = Conversation.objects.get(id=conversation_id, members=request.user)
        content = request.POST.get('message')
        if content:
            message = Message.objects.create(conversation=conversation, sender=request.user, content=content)
        return redirect('home/conversation_detail', conversation_id=conversation_id)

logger = logging.getLogger(__name__)
@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')  # Consider CSRF implications

@method_decorator(login_required, name='dispatch')

class ComposeMessageView(LoginRequiredMixin, View):
    template_name = 'home/compose_message.html'

    def get(self, request, *args, **kwargs):
        # Exclude the current user from the list of users to show in the recipient dropdown
        users = User.objects.exclude(id=request.user.id)
        # Initialize the form to be used in the template
        form = MessageForm()
        return render(request, self.template_name, {'users': users, 'form': form})

    def post(self, request, *args, **kwargs):
        # Determine if the request is AJAX and expecting JSON data
        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body)
            recipient_id = data.get('recipient')
            conversation_id = data.get('conversation_id')  # Add this line to define conversation_id
            conversation = Conversation.objects.get(id=conversation_id, members=request.user)
            return redirect('conversation_detail', conversation_id=conversation.id)
            
        else:
            recipient_id = request.POST.get('recipient')
            message_content = request.POST.get('message')

        if not recipient_id:
            logger.error('Recipient ID is missing from the request.')
            return JsonResponse({'error': 'Recipient user ID is missing.'}, status=400)

        try:
            recipient = User.objects.get(id=recipient_id)
            conversation, created = Conversation.objects.get_or_create_conversation(request.user, recipient)
            if created:
                logger.debug(f'New conversation created between {request.user.username} and {recipient.username}')
                conversation.last_updated = timezone.now()
                conversation.save()
            Message.objects.create(conversation=conversation, sender=request.user, content=message_content)
            return redirect('conversation_detail', conversation_id=conversation.id)  # Redirect to conversation detail
        except User.DoesNotExist:
            logger.error(f'User with id {recipient_id} does not exist.')
            return JsonResponse({'error': 'Recipient user does not exist.'}, status=404)
        except Exception as e:
            logger.exception(f'Unexpected error when composing message: {e}')
            return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)
