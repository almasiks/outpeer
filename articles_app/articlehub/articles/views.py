from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
def articles_list(request):
    return render(request, 'articles/article_list.html')


def article_detail(request, article_id):
    return HttpResponse(f'Это страница статьи с id: {article_id}')


def author_detail(request, author_id):
    return HttpResponse(f'Это страница автора с id: {author_id}')