from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/delete/', views.PostDeleteView.as_view, name='delete_post'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('category/<slug:category_slug>/',
         views.category_posts, name='category_posts'),
    path('profile/<slug:username_slug>/', views.profile, name='profile'),
    path('edit_profile/<int:pk>', views.UserUpdateView.as_view(), name='edit_profile'),
]
