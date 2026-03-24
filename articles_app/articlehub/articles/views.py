from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Article, Author
from .forms import DemoForm, ArticleModelForm , ArticleModelForm

def add_article(request):
    if request.method == 'POST':
        form = ArticleModelForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('article_list')

    form = ArticleModelForm()
    return render(request, 'articles/demo.html', {'form': form})



def demo_form_view(request):
    form = DemoForm()
    return render(request, 'articles/demo.html', context={'form': form})

@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleModelForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()

            return redirect('article_list')

    else:
        form = ArticleModelForm()

    return render(request, 'articles/article_create.html', {
        'form': form,
        'title': 'Create Article'
    })


def article_list(request):
    query = request.GET.get('q')
    articles = Article.objects.all()
    if query:

        articles = articles.filter(title__icontains=query)

    return render(request, 'articles/article_list.html', context={'articles': articles})
def article_detail(request, pk):
    article = get_object_or_404(Article, id = pk)
    return render(request, 'articles/article_detail.html', context={'article':article})

@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, id = pk, author = request.user)
    if request.method == 'POST':
        form = ArticleModelForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('article_list')
        pass
    else:
        form = ArticleModelForm(instance=article)

    return render(request, 'articles/article_create.html', {'form': form, 'title': 'Edit Article'})

@login_required()
def article_delete(request, pk):
    article = get_object_or_404(Article, id=pk, author = request.user)
    if request.method == 'POST':
        if request.method == 'POST':
            article.delete()

        return redirect('article_list')

    return render(request, 'articles/articles_confirm_delete.html', context={'article': article})