from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView

from django.conf import settings

User = get_user_model()


class RegisterView(CreateView):
  template_name = 'users/pages/register.html'
  form_class = UserCreationForm
  success_url = reverse_lazy('users:login')


class CustomLoginView(LoginView):
  template_name = 'users/pages/login.html'
  authentication_form = AuthenticationForm

  def get_success_url(self):
    next_url = self.request.GET.get('next', settings.DEFAULT_LOGIN_REDIRECT_URL)
    if next_url == settings.DEFAULT_LOGIN_REDIRECT_URL:
      return reverse_lazy(next_url, kwargs={'username': self.request.user.username})
    return next_url


class CustomLogoutView(LogoutView):
  next_page = reverse_lazy('blog:post_list')


def profile_view(request, username):
  user = get_object_or_404(User, username=username)
  posts = user.posts.order_by('-created_at')

  context = {
    'user': user,
    'posts': posts
  }

  return render(request, 'users/pages/profile.html', context)
