from django.urls import path

from . import views

urlpatterns = [
  path("posts/", views.get_post_list, name='post_list'),
  path("posts/<int:post_id>/", views.get_post_detail, name='post_detail'),
]
