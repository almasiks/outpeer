from django.shortcuts import render, redirect, get_object_or_404
from .models import Article, Author

def article_create(request):
    authors = Author.objects.all()
    context = {'authors': authors}

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        author_id = request.POST.get('author')


        if not title or not content or not author_id:
            return render(request, 'articles/article_create.html', context = {
                'error':'ALL fields must be filled!',
                'authors': authors,
            })

        # Создаем статью
        Article.objects.create(
            title=title,
            content=content,
            author_id=author_id
        )

        return redirect('article_list')

    return render(request, 'articles/article_create.html', context = {'authors' : authors})

def article_list(request):
    articles = Article.objects.all()
    return render(request, 'articles/article_list.html', context = {'articles' : articles})


def article_detail(request, pk):
    article = get_object_or_404(Article, id = pk)
    return render(request, 'articles/article_detail.html', context={'article':article})


def article_edit(request, pk):
    article = get_object_or_404(Article, id=pk)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        author_id = request.POST.get('author')

        if not title:
            return render(request, 'articles/article_create.html', context={
                'error': 'ALL fields must be filled!',
                'article': article,
            })
        article.title = title
        article.content = content
        article.save()

        return redirect('article_detail', pk)
    return render(request, 'articles/article_create.html', context={'article': article})


def article_delete(request, pk):
    article = get_object_or_404(Article, id=pk)
    if request.method == 'POST':
        article.delete()

        return redirect('article_list')

    return render(request, 'articles/articles_confirm_delete.html', context={'article': article})