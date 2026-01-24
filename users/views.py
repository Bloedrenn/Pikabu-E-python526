from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.list import MultipleObjectMixin

from django.conf import settings
from users.forms import CustomAuthenticationForm

User = get_user_model()


class RegisterView(CreateView):
  template_name = 'users/pages/register.html'
  form_class = UserCreationForm
  success_url = reverse_lazy('users:login')


class CustomLoginView(LoginView):
  template_name = 'users/pages/login.html'
  authentication_form = CustomAuthenticationForm

  def get_success_url(self):
    next_url = self.request.GET.get('next', settings.DEFAULT_LOGIN_REDIRECT_URL)
    if next_url == settings.DEFAULT_LOGIN_REDIRECT_URL:
      return reverse_lazy(next_url, kwargs={'username': self.request.user.username})
    return next_url


class CustomLogoutView(LogoutView):
  next_page = reverse_lazy('blog:post_list')


class ProfileView(DetailView, MultipleObjectMixin):
  model = User
  slug_url_kwarg = 'username'
  slug_field = 'username'
  template_name = 'users/pages/profile.html'
  paginate_by = 4
  # context_object_name = 'user' Необязательно

  def get_context_data(self, **kwargs):
    posts = self.object.posts.order_by('-created_at')

    # Заполняем queryset, чтобы django было что пагинировать
    context = super().get_context_data(object_list=posts, **kwargs)
    
    context['posts'] = context['object_list']
    del context['object_list']

    return context
