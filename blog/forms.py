from django import forms

from blog.models import Post


class PostForm(forms.ModelForm):
  class Meta:
    model = Post
    fields = ['title', 'category', 'text', 'image']
    widgets = {
      'title': forms.TextInput(attrs={
        'placeholder': "заголовок (максимальная длина 200 символов)"
      }),
      'category': forms.Select(attrs={'class': 'form-control'}),
      'image': forms.FileInput(attrs={'class': 'form-control'})
    }
    labels = {
      'title': 'Заголовок поста:',
      'category': 'Категория:',
      'text': 'Текст поста:',
      'image': 'Картинка поста'
    }
    help_texts = {
      'category': "- можно выбрать только одну категорию"
    }

  def clean_title(self):
    title = self.cleaned_data['title'].strip()

    if not title:
      raise forms.ValidationError("Заголовок обязателен.")
    
    if len(title) < 5:
      raise forms.ValidationError("Заголовок не должен быть короче 5 символов.")
    
    return title
