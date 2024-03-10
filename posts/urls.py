from django.urls import path
from posts import views
from . import views


urlpatterns = [
    path('', views.PostListView.as_view(), name='list'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PostUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete'),
    path('posts/<int:pk>/comment/', views.CommentCreateView.as_view(), name='comment'),
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('comment/<int:pk>/edit/', views.CommentUpdateView.as_view(), name='comment_update'),
    path('<int:pk>/like/', views.LikeUpdateView.as_view(), name='like'),
    path('new/', views.PostCreateView.as_view(), name='new'),
    path('like_ajax/<int:pk>/', views.like_toggle_ajax, name='like_ajax'),
    path('get_like_count/', views.get_like_count, name='get_like_count'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),


    
]
