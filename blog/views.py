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
  title = "Создать пост"
  submit_button_text = 'Создать'

  form = PostForm(request.POST or None)
  
  if request.method == "POST":
    if form.is_valid():
      post = form.save()

      return redirect('post_detail', post_id=post.id)
    # Если форма невалидна, продолжим к render ниже
  
  return render(request, 'blog/post_form.html', {"form": form, 'title': title, 'submit_button_text': submit_button_text})


def update_post(request, post_id):
  title = "Редактировать пост"
  submit_button_text = 'Обновить'

  post = get_object_or_404(Post, id=post_id)

  if request.method == "POST":
    form = PostForm(request.POST, instance=post)

    if form.is_valid():
      form.save()

      return redirect("post_detail", post_id=post.id)
    else:
      return render(request, 'blog/post_form.html', context={"form": form, 'title': title, 'submit_button_text': submit_button_text})

  form = PostForm(instance=post)

  return render(request, 'blog/post_form.html', context={"form": form, 'title': title, 'submit_button_text': submit_button_text})


def delete_post(request, post_id):
  post = get_object_or_404(Post, id=post_id)

  if request.method == "POST":
    post.delete()
    return redirect("post_list")
  
  return render(request, 'blog/confirm_post_delete.html', {'post': post})
