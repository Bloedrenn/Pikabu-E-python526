from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView

from django.conf import settings

User = get_user_model()


class RegisterView(CreateView):
  template_name = 'users/pages/register.html'
  form_class = UserCreationForm
  success_url = reverse_lazy('users:login')


def login_view(request):
  if request.method == "POST":
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
      login(request, form.get_user())

      next_url = request.GET.get('next', settings.DEFAULT_LOGIN_REDIRECT_URL) # next будет '/posts/add/', например
      if next_url == settings.DEFAULT_LOGIN_REDIRECT_URL:
        return redirect(next_url, request.user.username)
      else:
        return redirect(next_url)
    else:
      return render(request, 'users/pages/login.html', {'form': form})

  form = AuthenticationForm()

  return render(request, 'users/pages/login.html', {'form': form})


def logout_view(request):
  logout(request)
  return redirect("blog:post_list")


def profile_view(request, username):
  user = get_object_or_404(User, username=username)
  posts = user.posts.order_by('-created_at')

  context = {
    'user': user,
    'posts': posts
  }

  return render(request, 'users/pages/profile.html', context)
