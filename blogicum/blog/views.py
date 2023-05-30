from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blog.forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User

POSTS_ON_PAGE: int = 10


def get_published_posts():
    return Post.objects.select_related(
        'location', 'category', 'author'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        self.user = get_object_or_404(
            User,
            username=self.kwargs['username_slug']
        )

        if self.request.user == self.user:

            return Post.objects.select_related(
                'location', 'category', 'author'
            ).filter(author=self.user.id).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')

        return get_published_posts().filter(author=self.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username_slug': self.object.username}
        )


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    queryset = get_published_posts()
    paginate_by = POSTS_ON_PAGE


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username_slug': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', instance.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.object.id}
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return get_object_or_404(
            Post, pk=self.kwargs['pk'],
            author=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.object}
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        self.post_object = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_object.pk})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    # def form_valid(self, form):
    #     instance = get_object_or_404(Comment, pk=self.kwargs['pk'])
    #     if instance.author != self.request.user:
    #         return redirect('blog:post_detail', instance.post.id)
    #     return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', instance.post.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.object.post.id}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment, pk=self.kwargs['pk'],
            author=self.request.user
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.object.post.id}
        )


class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return get_published_posts().filter(category__slug=self.category.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
