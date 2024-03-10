from django.urls import path
from .views import SignUpView, ConversationListView, ConversationDetailView, ComposeMessageView, delete_conversation, reply_to_conversation
from . import views

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('create_profile/', views.CreateProfileView.as_view(), name='create_profile'),
    path('profile_edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('profile/', views.profile, name='my_profile'),
    path('follow/', views.FollowView.as_view(), name='follow'),
    path('followers/', views.FollowersView.as_view(), name='followers'),
    path('following/', views.FollowingView.as_view(), name='following'),
    path('get_following/', views.get_following, name='get_following'),
    path('get_followers/', views.get_followers, name='get_followers'),
    path('conversations/', ConversationListView.as_view(), name='conversation_list'),
    path('conversations/<int:conversation_id>/', ConversationDetailView.as_view(), name='conversation_detail'),
    path('delete_conversation/<int:conversation_id>/', views.delete_conversation, name='delete_conversation'),
    path('compose/', ComposeMessageView.as_view(), name='compose_message'),
    path('home/conversations/<int:conversation_id>/reply/', views.reply_to_conversation, name='reply_to_conversation'),


    
    

]
