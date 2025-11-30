from django.shortcuts import render, get_object_or_404, redirect

from blog.models import Post


def get_post_list(request):
  posts = Post.objects.all()

  return render(request, template_name='blog/post_list.html', context={'posts': posts})


def get_post_detail(request, post_id):
  # return render(request, 'blog/post_detail.html', {"post": Post.objects.get(id=post_id)})
  return render(request, 'blog/post_detail.html', {"post": get_object_or_404(Post, id=post_id)})


def create_post(request):
  if request.method == "GET":
    return render(request, 'blog/post_add.html')
  
  if request.method == "POST":
    title = request.POST.get('title').strip()
    text = request.POST.get('text').strip()

    errors = {}

    if not title:
      errors['title'] = 'Заголовок обязателен.'
    if not text:
      errors['text'] = 'Текст поста обязателено нужно указать.'

    if not errors:
      post = Post.objects.create(title=title, text=text)

      return redirect('post_detail', post_id=post.id)
    else:
      context = {
        'errors': errors,
        'title': title,
        'text': text
      }

      return render(request, 'blog/post_add.html', context)
