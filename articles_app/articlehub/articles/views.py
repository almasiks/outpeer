from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from articles.apps import ArticlesConfig


def articles_list(request):
    seacrh_query  = request.GET.get('seacrh')
    context = {
        'seacrh_query': seacrh_query,
    }

    return render(request, 'articles/article_list.html', context)


def article_detail(request, article_id):
    if article_id == 1:
         return HttpResponse(f'Это страница статьи с id: {article_id}')
    return Http404(f'статья с Id {article_id}')



def author_detail(request, author_id):
    seacrh_query = request.GET.get('seacrh')
    context = {
        'seacrh_query': seacrh_query,
    }
    if author_id == 1:
        return HttpResponse(f'Это страница автора с id: {author_id}')

    raise Http404
def article_create(request):
    request_post = request.POST

    if request.method == 'POST':
        title = request_post.get('title')
        content = request_post.get('content')
        return HttpResponse(f"Получена статья: {title}")

    return render(request, 'articles/article_create.html')


