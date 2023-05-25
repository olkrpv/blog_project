from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from blog.models import Category, Post, User, Comment
from .forms import PostForm, UserForm, CommentForm


POSTS_ON_PAGE: int = 10


def get_published_posts():
    return Post.objects.select_related(
        'location', 'category', 'author'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )


# def profile(request, username_slug):
#     template_name = 'blog/profile.html'
#
#     user_profile = get_object_or_404(User, username=username_slug)
#
#     author_posts = get_published_posts().filter(author=user_profile.id)
#
#     if user_profile == request.user:
#         author_posts = Post.objects.select_related(
#             'location', 'category', 'author'
#         ).filter(author=user_profile.id)
#
#     paginator = Paginator(author_posts, 10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     context = {'profile': user_profile, 'page_obj': page_obj}
#     return render(request, template_name, context)


class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author_posts = get_published_posts().filter(author=self.object.id)

        if self.object == self.request.user:
            author_posts = Post.objects.select_related(
                'location', 'category', 'author'
            ).filter(author=self.object.id)

        paginator = Paginator(author_posts, POSTS_ON_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['profile'] = self.object
        context['page_obj'] = page_obj
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserForm
    slug_field = 'username'
    slug_url_kwarg = 'username_slug'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username_slug': self.object.username}
        )

    def dispatch(self, request, *args, **kwargs):
        # Получаем объект по первичному ключу и автору или вызываем 404 ошибку.
        get_object_or_404(User, username=kwargs['username_slug'], id=request.user.id)
        return super().dispatch(request, *args, **kwargs)


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
        form.instance.pub_date = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
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
        return reverse_lazy(
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.object}
        return context

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', instance.post.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.object.post.id}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Comment, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.object.post.id}
        )


def category_posts(request, category_slug):
    template_name = 'blog/category.html'

    category = get_object_or_404(
        Category.objects.values('title', 'description'),
        slug=category_slug,
        is_published=True,
    )

    post_list = get_published_posts().filter(category__slug=category_slug)
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'category': category}
    return render(request, template_name, context)
