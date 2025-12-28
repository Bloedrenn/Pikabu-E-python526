from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from unidecode import unidecode

from blog.models import Post, Category, Tag
from blog.forms import PostForm


def get_post_list(request):
  posts = Post.objects.filter(status="published")

  return render(request, template_name='blog/pages/post_list.html', context={'posts': posts})


def get_category_posts(request, category_slug):
  category = get_object_or_404(Category, slug=category_slug)
  posts = Post.objects.filter(category=category, status='published')
  
  context = {
    'category': category,
    'posts': posts
  }
  return render(request, 'blog/pages/category_posts.html', context)


def get_tag_posts(request, tag_slug):
  tag = get_object_or_404(Tag, slug=tag_slug)
  posts = Post.objects.filter(tags=tag, status='published')

  return render(request, 'blog/pages/tag_posts.html', {
    'tag': tag,
    'posts': posts
  })


def get_post_detail(request, post_slug):
  # return render(request, 'blog/pages/post_detail.html', {"post": Post.objects.get(slug=post_slug)})
  return render(request, 'blog/pages/post_detail.html', {"post": get_object_or_404(Post, slug=post_slug)})


@login_required
def create_post(request):
  title = "Создать пост"
  submit_button_text = 'Создать'

  form = PostForm(request.POST or None, request.FILES or None)
  
  if request.method == "POST":
    if form.is_valid():
      post = form.save(commit=False)
      post.author = request.user
      post.slug = slugify(unidecode(post.title))
      post.save()

      tags = form.cleaned_data.get('tags_input')

      for tag_name in tags:
        tag, _ = Tag.objects.get_or_create(name=tag_name)
        post.tags.add(tag)

      return redirect('blog:post_detail', post_slug=post.slug)
    # Если форма невалидна, продолжим к render ниже
  
  return render(request, 'blog/pages/post_form.html', {"form": form, 'title': title, 'submit_button_text': submit_button_text})


def update_post(request, post_id):
  title = "Редактировать пост"
  submit_button_text = 'Обновить'

  post = get_object_or_404(Post, id=post_id)

  if (request.user != post.author):
    return render(request, 'blog/pages/not_allowed.html')

  if request.method == "POST":
    form = PostForm(request.POST, request.FILES, instance=post)

    if form.is_valid():
      form.save()

      tags = form.cleaned_data.get('tags_input')
      post.tags.clear()
      for tag_name in tags:
        tag, _ = Tag.objects.get_or_create(name=tag_name)
        post.tags.add(tag)

      return redirect("blog:post_detail", post_slug=post.slug)
    else:
      return render(request, 'blog/pages/post_form.html', context={"form": form, 'title': title, 'submit_button_text': submit_button_text})

  existing_tags = ", ".join(tag.name for tag in post.tags.all())
  form = PostForm(instance=post, initial={'tags_input': existing_tags})

  return render(request, 'blog/pages/post_form.html', context={"form": form, 'title': title, 'submit_button_text': submit_button_text})


def delete_post(request, post_id):
  post = get_object_or_404(Post, id=post_id)

  if (request.user != post.author):
    return render(request, 'blog/pages/not_allowed.html')

  if request.method == "POST":
    post.delete()
    return redirect("blog:post_list")
  
  return render(request, 'blog/pages/confirm_post_delete.html', {'post': post})


def main_page_view(request):
  return render(request, template_name='blog/pages/main_page.html')