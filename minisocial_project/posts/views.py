from tokenize import Comment

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from .models import Post
from django.shortcuts import redirect
from .models import Comment
from django.contrib.auth.decorators import login_required   
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm, CommentForm



def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'posts/post_list.html', {'posts': posts})

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    return render(request, 'posts/post_detail.html', {'post': post, 'comments': comments})

def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, author=request.user, text=content)
    return redirect('post_detail', post_id=post.id)

def user_posts(request, user_id):
    user = get_object_or_404(User, id=user_id)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    return render(request, 'posts/user_posts.html', {'posts': posts, 'user': user})

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        text = request.POST.get('content')
        if title and text:
            Post.objects.create(title=title, text=text, author=request.user)
            return redirect('post_list', post_id=Post.objects.last().id)
    return render(request, 'posts/create_post.html')

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        title = request.POST.get('title')
        text = request.POST.get('text')
        if title and text:
            post.title = title
            post.text = text
            post.save()
            return redirect('post_detail', post_id=post.id)
    return render(request, 'posts/edit_post.html', {'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        post.delete()
        return redirect('post_list')
    return render(request, 'posts/delete_post.html', {'post': post})


def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save()

            return redirect('post_detail', pk=post.pk)


    else:
        form = PostForm()

    return render(request, 'posts/create_post.html', {'form': form})