from django.shortcuts import render, get_object_or_404, redirect

from blog.models import Post
from blog.forms import PostForm


def get_post_list(request):
  posts = Post.objects.all()

  return render(request, template_name='blog/post_list.html', context={'posts': posts})


def get_post_detail(request, post_id):
  # return render(request, 'blog/post_detail.html', {"post": Post.objects.get(id=post_id)})
  return render(request, 'blog/post_detail.html', {"post": get_object_or_404(Post, id=post_id)})


def create_post(request):
  form = PostForm(request.POST or None)
  
  if request.method == "POST":
    if form.is_valid():
      post = Post.objects.create(
        title=form.cleaned_data['title'],
        text=form.cleaned_data['text']
      )

      return redirect('post_detail', post_id=post.id)
    # Если форма невалидна, продолжим к render ниже
  
  return render(request, 'blog/post_add.html', {"form": form})
