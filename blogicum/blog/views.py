from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from blog.models import Category, Post, User
from .forms import PostForm, UserForm


def get_published_posts():
    return Post.objects.select_related(
        'location', 'category', 'author'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )


def profile(request, username_slug):
    template_name = 'blog/profile.html'

    user_profile = get_object_or_404(
        User.objects.all(),
        username=username_slug
    )

    author_posts = get_published_posts().filter(author=user_profile.id)
    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'profile': user_profile, 'page_obj': page_obj}
    return render(request, template_name, context)


class PostListView(ListView):
    model = Post
    queryset = get_published_posts()
    paginate_by = 10
    template_name = 'blog/index.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.pub_date = timezone.now()
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = 'blog:index'


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')


def edit_profile(request):
    template_name = 'blog/user.html'
    form = UserForm
    context = {'form': form}
    return render(request, template_name, context)


def add_comment():
    pass


def post_detail(request, id):
    template_name = 'blog/detail.html'

    post = get_object_or_404(get_published_posts(), pk=id)

    context = {'post': post}
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'

    category = get_object_or_404(
        Category.objects.values('title', 'description'),
        slug=category_slug,
        is_published=True,
    )

    post_list = get_published_posts().filter(category__slug=category_slug)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'category': category}
    return render(request, template_name, context)
