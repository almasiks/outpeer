from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('user/<int:user_id>/posts/', views.user_posts, name='user_posts'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('create_post/', views.post_create, name='create_post'),
    path('<int:post_id>/comment/', views.add_comment, name='add_comments'),
]