from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
def articles_list(request):
    return render(request, 'articles/article_list.html')