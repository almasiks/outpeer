from django.urls import path
from . import views
urlpatterns = [
    path('', views.articles_list, name='articles_list'),
    path('<int:article_id>/', views.article_detail, name='article_detail'),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    path('create/', views.article_create, name='article_create'),
]
