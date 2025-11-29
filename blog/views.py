from django.shortcuts import render

from blog.models import Post


def get_post_list(request):
  posts = Post.objects.all()

  return render(request, template_name='blog/post_list.html', context={'posts': posts})
