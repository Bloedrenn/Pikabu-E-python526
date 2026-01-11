from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from blog.models import Post, Category, Tag
from blog.forms import PostForm


class PostListView(ListView):
  template_name = 'blog/pages/post_list.html'
  context_object_name = 'posts'
  queryset = Post.objects.filter(status="published").order_by('-created_at')
  paginate_by = 3


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


class CreatePostView(LoginRequiredMixin, CreateView):
  form_class = PostForm
  template_name = 'blog/pages/post_form.html'
  extra_context = {
    'title': "Создать пост",
    'submit_button_text': "Создать"
  }

  def form_valid(self, form):
    post = form.save(commit=False)
    post.author = self.request.user
    post.save()

    tags = form.cleaned_data.get('tags_input')
    for tag_name in tags:
      tag, _ = Tag.objects.get_or_create(name=tag_name)
      post.tags.add(tag)

    return redirect('blog:post_detail', post_slug=post.slug)


class PostUpdateView(UpdateView):
  model = Post
  pk_url_kwarg = 'post_id'  # потому что в url <int:post_id>, а не <int:id>
  form_class = PostForm
  template_name = 'blog/pages/post_form.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    context['title'] = "Редактировать пост"
    context['submit_button_text'] = "Обновить"
    context['form'].fields['tags_input'].initial = ", ".join(tag.name for tag in self.object.tags.all())
    
    return context

  def form_valid(self, form):
    if (self.request.user != self.object.author):
      return render(self.request, 'blog/pages/not_allowed.html')

    form.save()

    tags = form.cleaned_data.get('tags_input', [])
    self.object.tags.clear()
    for tag_name in tags:
      tag, _ = Tag.objects.get_or_create(name=tag_name)
      self.object.tags.add(tag)

    return redirect('blog:post_detail', post_slug=self.object.slug)


class PostDeleteView(LoginRequiredMixin, DeleteView):
  model = Post
  pk_url_kwarg = 'post_id'
  template_name = 'blog/pages/confirm_post_delete.html'
  # context_object_name = 'post' Необязательно
  success_url = reverse_lazy('blog:post_list')

  def dispatch(self, request, *args, **kwargs):
    # Получаем объект до любых действий
    self.object = self.get_object()
    
    # Проверяем права доступа
    if request.user != self.object.author:
      return render(request, 'blog/pages/not_allowed.html')
    
    return super().dispatch(request, *args, **kwargs)


class MainPageView(TemplateView):
  template_name = 'blog/pages/main_page.html'
