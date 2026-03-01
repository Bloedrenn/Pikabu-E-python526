from django.contrib import admin

from blog.models import News, Post, Category, Tag, Comment

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(News)
