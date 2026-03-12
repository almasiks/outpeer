from tkinter.constants import CASCADE

from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    isPublished = models.BooleanField(default=False)
    author = models.ForeignKey(Author, on_delete= models.CASCADE, related_name='articles' )




    def __str__(self):
        return self.title
