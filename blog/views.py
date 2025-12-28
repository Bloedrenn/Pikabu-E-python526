from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from unidecode import unidecode
from django.views.generic import ListView, DetailView

from blog.models import Post, Category, Tag
from blog.forms import PostForm


class PostListView(ListView):
  template_name = 'blog/pages/post_list.html'
  context_object_name = 'posts'
  queryset = Post.objects.filter(status="published")


class CategoryPostsView(ListView):
  template_name = 'blog/pages/category_posts.html'
  context_object_name = 'posts'

  def get_queryset(self):
    self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
    return Post.objects.filter(category=self.category, status='published')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    context['category'] = self.category
    
    return context


class TagPostsView(ListView):
  template_name = 'blog/pages/tag_posts.html'
  context_object_name = 'posts'

  def get_queryset(self):
    self.tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
    return Post.objects.filter(tags=self.tag, status='published')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    context['tag'] = self.tag

    return context


class PostDetailView(DetailView):
  model = Post
  slug_url_kwarg = 'post_slug'
  template_name = 'blog/pages/post_detail.html'
  # context_object_name = 'post' Необязательно
  # slug_field = 'slug' Необязательно


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