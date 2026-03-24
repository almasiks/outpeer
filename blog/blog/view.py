from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from myblog.models import Post


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_list.html', {'post': post})

