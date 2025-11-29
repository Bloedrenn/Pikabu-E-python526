from django.shortcuts import render, get_object_or_404

from blog.models import Post


def get_post_list(request):
  posts = Post.objects.all()

  return render(request, template_name='blog/post_list.html', context={'posts': posts})


def get_post_detail(request, post_id):
  # return render(request, 'blog/post_detail.html', {"post": Post.objects.get(id=post_id)})
  return render(request, 'blog/post_detail.html', {"post": get_object_or_404(Post, id=post_id)})
