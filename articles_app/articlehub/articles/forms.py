from django import forms
from django.forms import Select, SelectMultiple

from .models import Author, Article


class ArticleModelForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'author': forms.Select(attrs={'class': 'form-control'}),
            'categories': SelectMultiple(attrs={'class': 'form-select'}),

        }

class ValidationDemoForm(forms.Form):
    title = forms.CharField(label='title', max_length=100)
    content = forms.CharField(label='content', widget=forms.Textarea)
    is_published = forms.BooleanField(label='is_published', required=False)
    author = Select(attrs={'class': 'form-control'})
    rating = forms.IntegerField(label='rating', min_value=1, max_value=5)
    publish_at = forms.DateField(label='publish_at', required=False)



class DemoForm(forms.Form):
    char_field = forms.CharField(max_length=50, label='Текстовое поле', required=True)
    email_field = forms.EmailField(required=False, label='Email')
    url_field = forms.URLField(required=False, label='Ссылка')
    slug_field = forms.SlugField(label='Slug', required=True)
    textarea_field = forms.CharField(label='textarea_field', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}), required=False)
    integer_field = forms.IntegerField(label='integer_field', required=False, min_value=1)
    float_field = forms.FloatField(label='float_field', required=False)
    decimal_field = forms.DecimalField(label='decimal_field', required=False, max_digits=9, decimal_places=2) #financial values
    boolean_field = forms.BooleanField(label='boolean_field', required=False)
    choice_field = forms.ChoiceField(label='choice_field', required=False, choices=[('red','Красный')])
    multiple_ch_field = forms.MultipleChoiceField(label='multiple_ch_field', required=False, choices=[('red', 'Красный'), ('blue', 'синий'),('green','зеленый')])

    author_field = forms.Select(attrs={'class': 'form-control'})
    categories_field = Select(attrs={'class': 'form-control'})
    date_field = forms.DateField(label='date_field', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_time_field = forms.TimeField(label='date_time_field', required=False, widget=forms.TimeInput(attrs={'type': 'datetime-local'}))
    hidden_field = forms.CharField(label='hidden_field', required=False)

    def clean_title(self):
        title = self.cleaned_data['title']
        if 'Django' not in title:
            raise forms.ValidationError('should be a Django in name')
        return title
from datetime import datetime

def clean(self):
    cleaned_data = super().clean()

    title = cleaned_data['title']
    content = cleaned_data.get('content')
    is_published = cleaned_data.get('is_published')

    if is_published and is_published < datetime.now():
        self.add_error('published_at', 'Дата публикации не может быть в прошлом')

    if title and content and title == content:
        raise forms.ValidationError('content should not be same')
    return cleaned_data

