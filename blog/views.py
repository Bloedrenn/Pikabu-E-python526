from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q
from django.http import JsonResponse

from blog.models import Post, Category, Tag
from blog.forms import PostForm


class PostListView(ListView):
  template_name = 'blog/pages/post_list.html'
  context_object_name = 'posts'
  queryset = Post.objects.filter(status="published").order_by('-created_at')
  paginate_by = 3


class PostSearchView(ListView):
  template_name = "blog/pages/post_search.html"
  context_object_name = 'posts'
  paginate_by = 3

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['search_performed'] = any(self.request.GET.keys())
    return context
  
  def get_queryset(self):
    search_query = self.request.GET.get("search")

    if search_query:
      queryset = Post.objects.filter(status="published").order_by("-created_at")
      query = Q(title__icontains=search_query) | Q(text__icontains=search_query)

      search_category = self.request.GET.get("search_category")
      search_tag = self.request.GET.get("search_tag")
      if search_category:
        query |= Q(category__name__icontains=search_query)
      if search_tag:
        query |= Q(tags__name__icontains=search_query)

      return queryset.filter(query)
    
    return Post.objects.none()


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

  def get_object(self, queryset=None):
    post = super().get_object(queryset)

    user = self.request.user
    session_key = f'post_{post.id}_viewed' # "post_32_viewed"
    if not self.request.session.get(session_key, False) and post.author != user:
      Post.objects.filter(id=post.id).update(views=F("views") + 1)
      post.views = post.views + 1
      self.request.session[session_key] = True

    if user.is_authenticated and user != post.author and not post.viewed_users.filter(id=user.id).exists():
      post.viewed_users.add(user)

    return post

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    user = self.request.user
    post = self.object

    context['is_liked'] = False
    context['is_disliked'] = False
    
    if user.is_authenticated:
      context['is_liked'] = post.liked_users.filter(id=user.id).exists()
      context['is_disliked'] = post.disliked_users.filter(id=user.id).exists()

    context['likes_count'] = post.liked_users.count()
    context['dislikes_count'] = post.disliked_users.count()

    return context


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


def post_like_toggle_view(request, post_id):
  post = get_object_or_404(Post, id=post_id)
  user = request.user

  has_liked = post.liked_users.filter(id=user.id).exists()
  has_disliked = post.disliked_users.filter(id=user.id).exists()

  if has_liked:
    post.liked_users.remove(user)
    has_liked = False
  else:
    post.liked_users.add(user)
    has_liked = True

    if has_disliked:
      post.disliked_users.remove(user)
      has_disliked = False

  likes_count = post.liked_users.count()
  dislikes_count = post.disliked_users.count()

  return JsonResponse({
    'likes_count': likes_count,
    'dislikes_count': dislikes_count,
    'has_liked': has_liked,
    'has_disliked': has_disliked
  })


def post_dislike_toggle_view(request, post_id):
  post = get_object_or_404(Post, id=post_id)
  user = request.user

  has_disliked = post.disliked_users.filter(id=user.id).exists()
  has_liked = post.liked_users.filter(id=user.id).exists()

  if has_disliked:
    post.disliked_users.remove(user)
    has_disliked = False
  else:
    post.disliked_users.add(user)
    has_disliked = True

    if has_liked:
      post.liked_users.remove(user)
      has_liked = False

  dislikes_count = post.disliked_users.count()
  likes_count = post.liked_users.count()

  return JsonResponse({
    'dislikes_count': dislikes_count,
    'likes_count': likes_count,
    'has_disliked': has_disliked,
    'has_liked': has_liked
  })
