from multiprocessing import context
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.contrib.auth.mixins import (LoginRequiredMixin, UserPassesTestMixin)
from .models import Post, Comment, Like
from django.db.models import Count 
from django.http import JsonResponse
from .forms import CommentForm
from django.urls import reverse



class PostListView(ListView):
    model = Post
    template_name = 'posts/list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(like_count=Count('likes'))  # Fix the typo here
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_list'] = self.get_queryset()
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['post'] = post
        context['comments'] = post.comments.all()
        context['likes'] = post.likes.count()  # Count the number of likes
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'posts/new.html'
    fields = ['title','content']
    
    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'posts/edit.html'
    fields = ['title','content']

    def test_func(self):
        return self.get_object().author == self.request.user

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'posts/delete.html'
    success_url = reverse_lazy('list')

    def test_func(self):
        return self.get_object().author == self.request.user

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm  # Specify the form class
    template_name = 'posts/comment_form.html'
    success_url = reverse_lazy('list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])  # Get the post object from the URL kwargs
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.kwargs['pk']})
    
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'posts/comment_delete.html'
    success_url = reverse_lazy('list')

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user or comment.post.author == self.request.user

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.get_object().post.pk})
    
class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    fields = ['content']
    template_name = 'posts/comment_update.html'
    success_url = reverse_lazy('list')

    def test_func(self):
        comment = self.get_object()
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.get_object().post.pk})


def like_toggle_ajax(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user.is_authenticated:
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        like_count = post.likes.count()
        return JsonResponse({'liked': liked, 'like_count': like_count})
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=403)

def get_like_count(request):
    if request.method == 'GET':
        post_pk = request.GET.get('post_pk')
        try:
            post = Post.objects.get(pk=post_pk)
            like_count = post.likes.count()
            return JsonResponse({'like_count': like_count})
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

class LikeUpdateView(LoginRequiredMixin, CreateView):
    model = Like
    fields = []

    def form_valid(self, form):
        post = Post.objects.get(pk=self.kwargs['pk'])
        try:
            like = Like.objects.get(post=post, user=self.request.user)
            like.delete()
        except Like.DoesNotExist:
            Like.objects.create(post=post, user=self.request.user)
        return redirect(reverse('detail', kwargs={'pk': post.pk}))



