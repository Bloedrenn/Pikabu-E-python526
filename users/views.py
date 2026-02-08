from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.views.generic.list import MultipleObjectMixin
from django.contrib import messages

from django.conf import settings
from users.forms import CustomAuthenticationForm, CustomUserCreationForm

User = get_user_model()


class RegisterView(CreateView):
  template_name = 'users/pages/register.html'
  form_class = CustomUserCreationForm
  success_url = reverse_lazy('users:login')


class CustomLoginView(LoginView):
  template_name = 'users/pages/login.html'
  authentication_form = CustomAuthenticationForm

  def get_success_url(self):
    next_url = self.request.GET.get('next', settings.DEFAULT_LOGIN_REDIRECT_URL)
    if next_url == settings.DEFAULT_LOGIN_REDIRECT_URL:
      return reverse_lazy(next_url, kwargs={'username': self.request.user.username})
    return next_url
  
  def form_invalid(self, form):
    messages.warning(self.request, 'Ошибка входа!')

    return super().form_invalid(form)


class CustomLogoutView(LogoutView):
  next_page = reverse_lazy('blog:post_list')


class CustomPasswordChangeView(PasswordChangeView):
  template_name = 'users/pages/password_change.html'
  success_url = reverse_lazy('users:password_change_done')
  
  def form_valid(self, form):
    messages.success(self.request, 'Пароль успешно изменен!')
    return super().form_valid(form)


class PasswordChangeDoneView(TemplateView):
  template_name = 'users/pages/password_change_done.html'


class ProfileView(DetailView, MultipleObjectMixin):
  model = User
  slug_url_kwarg = 'username'
  slug_field = 'username'
  template_name = 'users/pages/index.html'
  paginate_by = 4
  context_object_name = 'user' # Теперь обязательно

  def get_context_data(self, **kwargs):
    posts = self.object.posts.order_by('-created_at')

    # Заполняем queryset, чтобы django было что пагинировать
    context = super().get_context_data(object_list=posts, **kwargs)
    
    context['posts'] = context['object_list']
    del context['object_list']

    return context


class FavoritePostsView(ListView):
  template_name = 'users/pages/favorite_posts.html'
  context_object_name = "posts"
  paginate_by = 2

  def get_queryset(self):
    return self.request.user.bookmarked_posts.all()
