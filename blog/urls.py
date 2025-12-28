from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
  path("posts/", views.PostListView.as_view(), name='post_list'),
  path('posts/category/<slug:category_slug>/', views.CategoryPostsView.as_view(), name="category_posts"),
  path('posts/tag/<slug:tag_slug>/', views.TagPostsView.as_view(), name="tag_posts"),
  path('posts/add/', views.create_post, name="new_post"),
  path('posts/<int:post_id>/edit/', views.update_post, name="edit_post"),
  path('posts/<int:post_id>/delete/', views.delete_post, name="remove_post"),
  path('posts/<slug:post_slug>/', views.get_post_detail, name="post_detail"),
  path('', views.main_page_view, name='main_page'),
]
